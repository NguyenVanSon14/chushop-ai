"""Seed script for ChủShop AI Money Brain Demo Data (M8).

Generates a realistic business with ~25 products, ~600 sales orders across 2
channels (SHOPEE, TIKTOK), operating expenses, and deterministic financial
metrics across 2 months.
"""

import os
import random
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.modules.businesses.model import Business, BusinessMember, BusinessRole
from app.modules.expenses.model import Expense
from app.modules.products.model import Product
from app.modules.sales.model import SalesOrder, SalesOrderItem
from app.modules.users.model import User

DEMO_USER_EMAIL = "demo@chushop.ai"
DEMO_BUSINESS_NAME = "Thời Trang ChủShop Demo"
DEMO_BUSINESS_SLUG = "thoi-trang-chushop-demo"

# 25 Products with varying margins and 1 loss-making high-volume product
PRODUCTS_DATA = [
    # (name, sku, selling_price, cost_price)
    ("Áo Sơ Mi Nam Công Sở Premium", "SM-001", 350_000, 150_000),
    ("Áo Thun Cotton Form Rộng Uniseх", "AT-002", 190_000, 80_000),
    ("Quần Jeans Nữ Lưng Cao", "QJ-003", 420_000, 210_000),
    ("Váy Xòe Dáng Dài Dự Tiệc", "VX-004", 550_000, 250_000),
    ("Áo Khoác Denim Vintage", "AK-005", 680_000, 320_000),
    ("Quần Tây Nam Dáng Hàn Quốc", "QT-006", 390_000, 180_000),
    ("Chân Váy Bút Chữ A", "CV-007", 280_000, 120_000),
    ("Áo Polo Nam Co Giãn 4 Chiều", "AP-008", 290_000, 130_000),
    ("Đầm Suông Cổ V Công Sở", "DS-009", 480_000, 220_000),
    ("Áo Cardigan Len Mỏng", "AC-010", 320_000, 160_000),
    # Low margin products
    ("Tất Cổ Cao Cotton (Hộp 5 đôi)", "TC-011", 79_000, 65_000),
    ("Nón Cót Rộng Vành Đi Biển", "NC-012", 99_000, 85_000),
    ("Dây Lưng Da Bò Basic", "DL-013", 150_000, 125_000),
    ("Khăn Choàng Cổ Lụa Tơ Tằm", "KC-014", 180_000, 155_000),
    ("Mũ Nồi Beret Thời Trang", "MN-015", 120_000, 100_000),
    # High volume LOSS-MAKING product (Triển khai chương trình Xả Kho Lỗ)
    ("Áo Khoác Combo Xả Hàng Lỗ", "AK-LOSS", 150_000, 230_000),
    # More balanced products
    ("Áo Len Cổ Lọ Unisex", "AL-017", 340_000, 170_000),
    ("Quần Short Kaki Nam", "QS-018", 220_000, 110_000),
    ("Đầm Max Lụa Dạo Phố", "DM-019", 620_000, 300_000),
    ("Áo Blazer Nữ 2 Lớp", "AB-020", 750_000, 360_000),
    ("Quần Jogger Thể Thao Nam", "QJ-021", 260_000, 130_000),
    ("Áo Croptop Nữ Cá Tính", "AC-022", 160_000, 75_000),
    ("Chân Váy Xếp Ly Dáng Dài", "CV-023", 310_000, 140_000),
    ("Áo Ghile Len Style Hàn", "AG-024", 270_000, 120_000),
    ("Bộ Pyjama Lụa Mặc Nhà", "BP-025", 380_000, 190_000),
]


def seed_data(session: Session) -> dict[str, object]:
    random.seed(2026)  # Deterministic seed

    # 1. User
    user = session.scalar(select(User).where(User.email == DEMO_USER_EMAIL))
    if not user:
        user = User(
            email=DEMO_USER_EMAIL,
            full_name="Chủ Shop Demo",
            password_hash=hash_password("DemoPass123!"),
            is_active=True,
        )
        session.add(user)
        session.flush()

    # 2. Business
    business = session.scalar(select(Business).where(Business.slug == DEMO_BUSINESS_SLUG))
    if business:
        # Clean existing demo data for clean re-seeding
        session.delete(business)
        session.flush()

    business = Business(
        name=DEMO_BUSINESS_NAME,
        slug=DEMO_BUSINESS_SLUG,
        currency="VND",
        timezone="Asia/Ho_Chi_Minh",
    )
    session.add(business)
    session.flush()

    member = BusinessMember(
        user_id=user.id,
        business_id=business.id,
        role=BusinessRole.OWNER,
    )
    session.add(member)

    # 3. Products
    created_products: list[Product] = []
    for name, sku, price, cost in PRODUCTS_DATA:
        p = Product(
            business_id=business.id,
            name=name,
            sku=sku,
            selling_price=price,
            cost_price=cost,
            is_active=True,
        )
        session.add(p)
        created_products.append(p)
    session.flush()

    # Map products by SKU
    loss_product = next(p for p in created_products if p.sku == "AK-LOSS")
    normal_products = [p for p in created_products if p.sku != "AK-LOSS"]

    # Dates spanning 2 months: Previous Month (Aug 2026) and Current Month (Sep 2026)
    # Target total ~650 orders
    channels = ["SHOPEE", "TIKTOK"]

    orders_count = 0
    total_revenue = 0
    total_cogs = 0
    total_fees = 0

    # 4. Generate Sales Orders
    for day_offset in range(60):
        # Date range from 2026-08-01 to 2026-09-29
        order_date = datetime(2026, 8, 1, 10, 0, 0, tzinfo=ZoneInfo("Asia/Ho_Chi_Minh")) + timedelta(days=day_offset)
        utc_ordered_at = order_date.astimezone(UTC)

        # 10 to 12 orders per day
        daily_order_num = random.randint(10, 12)
        for i in range(daily_order_num):
            orders_count += 1
            channel = random.choice(channels)
            ext_id = f"ORD-{order_date.strftime('%Y%m%d')}-{i+1:03d}"

            # Shopee fees ~8-12%, TikTok fees ~10-14% plus fixed shipping/affiliate
            base_fee = 15_000 if channel == "SHOPEE" else 22_000

            order = SalesOrder(
                business_id=business.id,
                sales_import_id=None,
                external_id=ext_id,
                channel=channel,
                ordered_at=utc_ordered_at,
                fees=base_fee,
            )
            session.add(order)
            session.flush()
            total_fees += base_fee

            # Decide items: 30% chance to include loss product to ensure high volume for it
            items_to_add: list[tuple[Product, int]] = []
            if random.random() < 0.35:
                items_to_add.append((loss_product, random.randint(1, 3)))
            
            # Add 1-2 regular products
            reg_selected = random.sample(normal_products, random.randint(1, 2))
            for rp in reg_selected:
                items_to_add.append((rp, random.randint(1, 2)))

            for prod, qty in items_to_add:
                item_rev = qty * prod.selling_price
                item_cogs = qty * prod.cost_price
                total_revenue += item_rev
                total_cogs += item_cogs

                item = SalesOrderItem(
                    sales_order_id=order.id,
                    product_id=prod.id,
                    product_name_snapshot=prod.name,
                    sku_snapshot=prod.sku or "",
                    quantity=qty,
                    unit_price=prod.selling_price,
                    cost_price_snapshot=prod.cost_price,
                )
                session.add(item)

    # 5. Operating Expenses
    expenses_data = [
        # August 2026
        ("Tiền thuê mặt bằng tháng 8", "Mặt bằng", 15_000_000, date(2026, 8, 1)),
        ("Lương nhân viên bán hàng tháng 8", "Lương", 25_000_000, date(2026, 8, 5)),
        ("Chi phí Quảng cáo TikTok Ads tháng 8", "Marketing", 18_000_000, date(2026, 8, 10)),
        ("Chi phí Điện nước & Internet tháng 8", "Vận hành", 3_500_000, date(2026, 8, 15)),
        ("Chi phí Bao bì & Đóng gói tháng 8", "Vật tư", 4_200_000, date(2026, 8, 20)),
        # September 2026
        ("Tiền thuê mặt bằng tháng 9", "Mặt bằng", 15_000_000, date(2026, 9, 1)),
        ("Lương nhân viên bán hàng tháng 9", "Lương", 25_000_000, date(2026, 9, 5)),
        ("Chi phí Quảng cáo Shopee & TikTok Ads tháng 9", "Marketing", 22_000_000, date(2026, 9, 10)),
        ("Chi phí Điện nước & Internet tháng 9", "Vận hành", 3_800_000, date(2026, 9, 15)),
        ("Chi phí Bao bì & Đóng gói tháng 9", "Vật tư", 5_000_000, date(2026, 9, 20)),
    ]

    total_expenses = 0
    for desc, cat, amount, incurred in expenses_data:
        exp = Expense(
            business_id=business.id,
            description=desc,
            category=cat,
            amount=amount,
            incurred_on=incurred,
        )
        session.add(exp)
        total_expenses += amount

    session.commit()

    return {
        "user_email": user.email,
        "business_id": str(business.id),
        "business_name": business.name,
        "products_count": len(created_products),
        "orders_count": orders_count,
        "total_revenue": total_revenue,
        "total_cogs": total_cogs,
        "total_fees": total_fees,
        "total_expenses": total_expenses,
        "gross_profit": total_revenue - total_cogs,
        "net_profit": (total_revenue - total_cogs) - total_fees - total_expenses,
    }


def main() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        result = seed_data(session)
        print("=== DEMO DATA SEEDED SUCCESSFULLY ===")
        for k, v in result.items():
            if isinstance(v, int) and "count" not in k:
                print(f"{k}: {v:,} VND")
            else:
                print(f"{k}: {v}".encode("ascii", "replace").decode("ascii"))


if __name__ == "__main__":
    main()
