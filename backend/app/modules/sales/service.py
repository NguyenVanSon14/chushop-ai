import csv
import hashlib
import io
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from openpyxl import load_workbook
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.businesses.access import require_business_manager, require_business_member
from app.modules.businesses.model import Business
from app.modules.sales.model import SalesImport, SalesOrder, SalesOrderItem
from app.modules.sales.repository import SalesRepository
from app.modules.sales.schema import (
    ImportPreview,
    ImportPreviewRow,
    ManualSalesOrderCreate,
    RawImportRow,
    SalesOrderItemRead,
    SalesOrderRead,
)
from app.modules.users.model import User

REQUIRED_COLUMNS = {
    "order_code",
    "channel",
    "ordered_at",
    "sku",
    "quantity",
    "unit_price",
    "fees",
}
MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_ROWS = 10_000


class SalesService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sales = SalesRepository(db)

    def preview(
        self, *, business_id: UUID, filename: str, content: bytes, user: User
    ) -> ImportPreview:
        require_business_manager(self.db, business_id=business_id, user=user)
        rows = self._resolve_rows(business_id=business_id, filename=filename, content=content)
        return self._build_preview(filename=filename, rows=rows)

    def import_file(
        self, *, business_id: UUID, filename: str, content: bytes, user: User
    ) -> SalesImport:
        require_business_manager(self.db, business_id=business_id, user=user)
        content_hash = hashlib.sha256(content).hexdigest()
        if self.sales.import_exists(business_id=business_id, content_hash=content_hash):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tệp này đã được nhập trước đó",
            )
        rows = self._resolve_rows(business_id=business_id, filename=filename, content=content)
        self._validate_orders(rows)
        products = self.sales.products_by_sku(
            business_id=business_id, skus={row.sku for row in rows}
        )
        grouped: dict[tuple[str, str], list[ImportPreviewRow]] = defaultdict(list)
        for row in rows:
            grouped[(row.channel, row.order_code)].append(row)
        try:
            import_record = self.sales.add_import(
                business_id=business_id,
                filename=filename,
                content_hash=content_hash,
                row_count=len(rows),
            )
            for (channel, order_code), order_rows in grouped.items():
                first = order_rows[0]
                order = self.sales.add_order(
                    business_id=business_id,
                    sales_import_id=import_record.id,
                    external_id=order_code,
                    channel=channel,
                    ordered_at=first.ordered_at,
                    fees=first.fees,
                )
                for row in order_rows:
                    self.sales.add_item(
                        sales_order_id=order.id,
                        product=products[row.sku],
                        quantity=row.quantity,
                        unit_price=row.unit_price,
                    )
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tệp chứa đơn hàng đã tồn tại",
            ) from None
        return import_record

    def list_orders(self, *, business_id: UUID, user: User) -> list[SalesOrderRead]:
        require_business_member(self.db, business_id=business_id, user=user)
        orders = self.sales.list_orders(business_id)
        items = self.sales.items_for_orders([order.id for order in orders])
        by_order: dict[UUID, list[SalesOrderItem]] = defaultdict(list)
        for item in items:
            by_order[item.sales_order_id].append(item)
        return [self._order_read(order, by_order[order.id]) for order in orders]

    def delete_order(self, *, business_id: UUID, order_id: UUID, user: User) -> None:
        require_business_manager(self.db, business_id=business_id, user=user)
        order = self.sales.get_order(order_id=order_id, business_id=business_id)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy đơn hàng",
            )
        self.sales.delete_order(order)
        self.db.commit()

    def delete_import(self, *, business_id: UUID, import_id: UUID, user: User) -> None:
        require_business_manager(self.db, business_id=business_id, user=user)
        record = self.sales.get_import(import_id=import_id, business_id=business_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy bản nhập",
            )
        orders = self.sales.orders_by_import(import_id)
        for order in orders:
            self.sales.delete_order(order)
        self.sales.delete_import(record)
        self.db.commit()

    def create_order(
        self, *, business_id: UUID, payload: ManualSalesOrderCreate, user: User
    ) -> SalesOrderRead:
        require_business_manager(self.db, business_id=business_id, user=user)
        business = self.db.get(Business, business_id)
        if business is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy doanh nghiệp")
        product_ids = {item.product_id for item in payload.items}
        products = self.sales.products_by_id(
            business_id=business_id,
            product_ids=product_ids,
        )
        missing = product_ids - products.keys()
        if missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Có sản phẩm không thuộc doanh nghiệp hoặc không còn tồn tại",
            )
        inactive = [
            products[item.product_id].name
            for item in payload.items
            if not products[item.product_id].is_active
        ]
        if inactive:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Sản phẩm đang tạm ẩn: {', '.join(inactive)}",
            )
        ordered_at = payload.ordered_at
        if ordered_at.tzinfo is None:
            ordered_at = ordered_at.replace(tzinfo=ZoneInfo(business.timezone))
        ordered_at = ordered_at.astimezone(UTC)
        order_code = payload.order_code or f"MANUAL-{uuid4().hex[:12].upper()}"
        try:
            order = self.sales.add_order(
                business_id=business_id,
                sales_import_id=None,
                external_id=order_code,
                channel=payload.channel,
                ordered_at=ordered_at,
                fees=payload.fees,
            )
            items = [
                self.sales.add_item(
                    sales_order_id=order.id,
                    product=products[item.product_id],
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in payload.items
            ]
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Mã đơn đã tồn tại trên kênh bán này",
            ) from None
        return self._order_read(order, items)

    def _resolve_rows(
        self, *, business_id: UUID, filename: str, content: bytes
    ) -> list[ImportPreviewRow]:
        raw_rows = self._parse_file(filename=filename, content=content)
        parsed_rows = [self._validate_row(row, index + 2) for index, row in enumerate(raw_rows)]
        products = self.sales.products_by_sku(
            business_id=business_id, skus={row.sku for row in parsed_rows}
        )
        missing = sorted({row.sku for row in parsed_rows} - products.keys())
        if missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Không tìm thấy SKU: {', '.join(missing[:10])}",
            )
        rows = [
            ImportPreviewRow(
                order_code=row.order_code,
                channel=row.channel,
                ordered_at=self._normalize_datetime(row.ordered_at),
                sku=row.sku,
                product_name=products[row.sku].name,
                quantity=row.quantity,
                unit_price=row.unit_price,
                cost_price_snapshot=products[row.sku].cost_price,
                fees=row.fees,
            )
            for row in parsed_rows
        ]
        self._validate_orders(rows)
        return rows

    def _parse_file(self, *, filename: str, content: bytes) -> list[dict[str, object]]:
        if not content:
            raise HTTPException(status_code=422, detail="Tệp không có dữ liệu")
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Tệp vượt quá giới hạn 5 MB")
        suffix = Path(filename).suffix.lower()
        if suffix == ".csv":
            try:
                text = content.decode("utf-8-sig")
            except UnicodeDecodeError:
                raise HTTPException(status_code=422, detail="CSV phải sử dụng UTF-8") from None
            reader = csv.DictReader(io.StringIO(text))
            headers = set(reader.fieldnames or [])
            rows: list[dict[str, object]] = list(reader)
        elif suffix == ".xlsx":
            try:
                workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
                sheet = workbook.active
                iterator = sheet.iter_rows(values_only=True)
                header_row = next(iterator, None)
                headers = {str(value).strip() for value in header_row or [] if value is not None}
                header_list = [
                    str(value).strip() if value is not None else "" for value in header_row or []
                ]
                rows = [dict(zip(header_list, values, strict=False)) for values in iterator]
                workbook.close()
            except Exception:
                raise HTTPException(status_code=422, detail="Không thể đọc tệp XLSX") from None
        else:
            raise HTTPException(status_code=422, detail="Chỉ hỗ trợ tệp CSV hoặc XLSX")
        missing_columns = sorted(REQUIRED_COLUMNS - headers)
        if missing_columns:
            raise HTTPException(
                status_code=422,
                detail=f"Thiếu cột: {', '.join(missing_columns)}",
            )
        rows = [row for row in rows if any(value not in (None, "") for value in row.values())]
        if not rows:
            raise HTTPException(status_code=422, detail="Tệp không có dòng dữ liệu")
        if len(rows) > MAX_ROWS:
            raise HTTPException(status_code=413, detail="Tệp vượt quá giới hạn 10.000 dòng")
        return rows

    def _validate_row(self, row: dict[str, object], line_number: int) -> RawImportRow:
        try:
            return RawImportRow.model_validate(
                {
                    "order_code": str(row.get("order_code") or ""),
                    "channel": str(row.get("channel") or "").upper(),
                    "ordered_at": row.get("ordered_at"),
                    "sku": str(row.get("sku") or "").strip().upper(),
                    "quantity": self._parse_int(row.get("quantity")),
                    "unit_price": self._parse_int(row.get("unit_price")),
                    "fees": self._parse_int(row.get("fees")),
                }
            )
        except (ValidationError, ValueError):
            raise HTTPException(
                status_code=422, detail=f"Dữ liệu không hợp lệ tại dòng {line_number}"
            ) from None

    @staticmethod
    def _parse_int(value: object) -> int:
        if isinstance(value, bool):
            raise ValueError
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        text = str(value).strip()
        if not text or any(character in text for character in ".,eE"):
            raise ValueError
        return int(text)

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=ZoneInfo("Asia/Ho_Chi_Minh"))
        return value.astimezone(UTC)

    @staticmethod
    def _validate_orders(rows: list[ImportPreviewRow]) -> None:
        seen: dict[tuple[str, str], tuple[datetime, int]] = {}
        for row in rows:
            key = (row.channel, row.order_code)
            values = (row.ordered_at, row.fees)
            if key in seen and seen[key] != values:
                raise HTTPException(
                    status_code=422,
                    detail=f"Đơn {row.order_code} có ngày hoặc phí không nhất quán",
                )
            seen[key] = values

    def _build_preview(self, *, filename: str, rows: list[ImportPreviewRow]) -> ImportPreview:
        orders = {(row.channel, row.order_code): row.fees for row in rows}
        return ImportPreview(
            filename=filename,
            row_count=len(rows),
            order_count=len(orders),
            total_revenue=sum(row.revenue for row in rows),
            total_cost=sum(row.cost for row in rows),
            total_fees=sum(orders.values()),
            rows=rows[:100],
        )

    @staticmethod
    def _order_read(order: SalesOrder, items: list[SalesOrderItem]) -> SalesOrderRead:
        item_reads = [
            SalesOrderItemRead(
                id=item.id,
                product_id=item.product_id,
                product_name_snapshot=item.product_name_snapshot,
                sku_snapshot=item.sku_snapshot,
                quantity=item.quantity,
                unit_price=item.unit_price,
                cost_price_snapshot=item.cost_price_snapshot,
                revenue=item.quantity * item.unit_price,
                cogs=item.quantity * item.cost_price_snapshot,
            )
            for item in items
        ]
        revenue = sum(item.revenue for item in item_reads)
        cogs = sum(item.cogs for item in item_reads)
        return SalesOrderRead(
            id=order.id,
            business_id=order.business_id,
            external_id=order.external_id,
            channel=order.channel,
            ordered_at=order.ordered_at,
            fees=order.fees,
            revenue=revenue,
            cogs=cogs,
            items=item_reads,
        )
