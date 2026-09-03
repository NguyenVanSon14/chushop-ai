# Trợ lý Money Brain M5

Luồng xử lý:

```text
Câu hỏi người dùng
→ phân loại ý định
→ analytics tool được phép
→ kết quả có cấu trúc từ Python
→ provider giải thích
→ lưu hội thoại
```

Trợ lý hỗ trợ các nhóm câu hỏi nghiệm thu:

- lợi nhuận ròng trong kỳ;
- sản phẩm có lợi nhuận gộp cao nhất;
- sản phẩm đang bán lỗ;
- khoản chi phí lớn nhất;
- nguyên nhân lợi nhuận giảm so với kỳ trước;
- lợi nhuận đóng góp theo kênh bán.

Mọi tool đều xác thực `BusinessMember` và chỉ đọc dữ liệu thuộc doanh nghiệp trong URL. Tool gọi `AnalyticsService`; model giải thích không được truy cập database và không tự tạo số liệu tài chính.

Provider mặc định là `DeterministicExplanationProvider`, giúp dự án hoạt động local mà không cần secret hay dịch vụ bên ngoài. `ExplanationProvider` là ranh giới để cắm nhà cung cấp LLM sau khi có quyết định riêng về provider, model, ngân sách và quản lý API key.
