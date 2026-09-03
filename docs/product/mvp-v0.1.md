# Money Brain v0.1

ChủShop AI giúp doanh nghiệp nhỏ và người bán hàng online Việt Nam biến dữ liệu kinh doanh thành phân tích tài chính rõ ràng.

M0-M5 hiện gồm:

- nền tảng FastAPI, PostgreSQL và Next.js;
- đăng ký, đăng nhập và hồ sơ người dùng;
- doanh nghiệp đa tenant với kiểm tra `BusinessMember`;
- quản lý sản phẩm;
- xem trước và nhập đơn bán hàng từ CSV/XLSX;
- quản lý chi phí;
- dashboard Money Brain theo khoảng ngày, kỳ so sánh, xu hướng ngày, sản phẩm và kênh bán.
- trợ lý tài chính có hội thoại, lịch sử và các analytics tool được phép.

Giá trị tiền được lưu bằng số nguyên VND. Giá vốn lịch sử được chụp tại thời điểm import. Backend là nguồn có thẩm quyền cho mọi công thức tài chính.

Trợ lý hiện dùng bộ giải thích xác định chạy local qua một provider abstraction. Việc kết nối nhà cung cấp LLM bên ngoài và tích hợp trực tiếp với các kênh bán chưa nằm trong phần đã triển khai.
