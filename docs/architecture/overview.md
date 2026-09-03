# Kiến trúc ChủShop AI

```text
Next.js + TypeScript → REST API → FastAPI + Python → PostgreSQL
```

Backend sở hữu xác thực, phân quyền, tenant isolation, persistence và mọi phép tính tài chính có thẩm quyền. Luồng backend là Router → Service → Repository → Database; thay đổi schema dùng Alembic.

Frontend sở hữu giao diện tiếng Việt và tương tác người dùng. Luồng frontend là Page → Feature → Hook → API Client → Backend; TanStack Query quản lý server state và HTTP được tập trung trong `lib/api`.

Tenant access theo User → BusinessMember → Business → Resource. ID doanh nghiệp từ client không tự tạo ra quyền truy cập. M0/M1 dùng Bearer access token; token hết hạn theo cấu hình môi trường.
