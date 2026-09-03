# Quy tắc tài chính

- Lưu VND có thẩm quyền dưới dạng số nguyên: `299000` nghĩa là 299.000 VND. Không dùng float.
- Python backend tính các chỉ số tài chính; frontend chỉ hiển thị và LLM chỉ giải thích kết quả có cấu trúc.
- Mỗi `SalesOrderItem` lưu `cost_price_snapshot`. Thay đổi giá vốn hiện tại của `Product` không được viết lại lợi nhuận lịch sử.
- Mọi phép tính doanh thu, giá vốn, phí, lợi nhuận và biên lợi nhuận phải có test xác định.

## Công thức Money Brain M4

Các tổng số được tính cho khoảng ngày được chọn theo múi giờ của doanh nghiệp:

```text
doanh_thu = tổng(số_lượng × đơn_giá)
giá_vốn = tổng(số_lượng × giá_vốn_snapshot)
lợi_nhuận_gộp = doanh_thu - giá_vốn
lợi_nhuận_ròng = lợi_nhuận_gộp - phí_bán_hàng - chi_phí_vận_hành
```

Biên lợi nhuận được API trả về theo basis point và làm tròn `ROUND_HALF_UP`:

```text
biên_bps = lợi_nhuận × 10.000 / doanh_thu
10.000 bps = 100%
```

Nếu doanh thu bằng 0, biên lợi nhuận là `null`. Kỳ trước có cùng số ngày và kết thúc ngay trước kỳ hiện tại. Tỷ lệ thay đổi dùng trị tuyệt đối của kỳ trước làm mẫu số; nếu giá trị kỳ trước bằng 0 thì tỷ lệ thay đổi là `null`.

Lợi nhuận đóng góp theo kênh bằng doanh thu trừ giá vốn và phí bán hàng. Chi phí vận hành chưa được phân bổ theo kênh hoặc sản phẩm trong v0.1.
