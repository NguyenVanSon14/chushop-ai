# Dữ liệu bán hàng M3/M5

Trang Bán hàng hỗ trợ hai cách ghi nhận dữ liệu.

## Nhập thủ công

Phù hợp khi shop không xuất được file hoặc chỉ có một số đơn mỗi ngày. Người dùng nhập:

- mã đơn, có thể để trống để backend tự tạo;
- kênh và thời gian bán;
- phí bán hàng bằng số nguyên VND;
- một hoặc nhiều sản phẩm, số lượng và đơn giá thực bán.

Sản phẩm phải thuộc cùng doanh nghiệp và đang hoạt động. Backend tự lấy tên, SKU và giá vốn hiện tại vào `cost_price_snapshot`, sau đó tự tính doanh thu và giá vốn. Mã đơn không được trùng trong cùng một kênh bán.

## Nhập CSV/XLSX

Hỗ trợ tệp `.csv` UTF-8 và `.xlsx`, tối đa 5 MB hoặc 10.000 dòng. Dòng đầu tiên phải có đúng các cột sau:

```text
order_code,channel,ordered_at,sku,quantity,unit_price,fees
```

Ví dụ:

```csv
order_code,channel,ordered_at,sku,quantity,unit_price,fees
DH-001,SHOPEE,2026-09-01T10:00:00+07:00,SP-001,2,299000,15000
DH-002,TIKTOK,2026-09-02T11:00:00+07:00,SP-002,1,450000,10000
```

- `sku` phải tồn tại trong danh mục sản phẩm của cùng doanh nghiệp.
- `quantity` là số nguyên dương. `unit_price` và `fees` là số nguyên VND không âm.
- Nếu một đơn có nhiều dòng sản phẩm, lặp lại `order_code`, `channel`, `ordered_at` và cùng giá trị `fees` trên mỗi dòng. Phí chỉ được tính một lần cho đơn.
- Thời gian không kèm múi giờ được hiểu là `Asia/Ho_Chi_Minh`, sau đó lưu UTC.
- Khi xác nhận import, backend lấy giá vốn sản phẩm tại thời điểm đó vào `cost_price_snapshot`.
- Cùng nội dung tệp hoặc cùng `channel + order_code` trong một doanh nghiệp sẽ bị từ chối để chống trùng.
