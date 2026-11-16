# ChủShop AI

Nền tảng SaaS Money Brain v0.1 cho chủ shop và doanh nghiệp nhỏ Việt Nam. M0-M6 hiện cung cấp xác thực, doanh nghiệp đa tenant, sản phẩm, nhập bán hàng, quản lý chi phí, dashboard phân tích tài chính, trợ lý giải thích số liệu và sửa/xóa dữ liệu bán hàng sai.

## Chuẩn bị

Yêu cầu Python 3.12+ và Node.js 22.13+. Sao chép `.env.example` thành `.env` ở thư mục gốc. Backend đọc biến môi trường từ thư mục đang chạy; khi phát triển, sao chép cùng file vào `backend/.env`. `SECRET_KEY` là bắt buộc và phải được thay bằng chuỗi ngẫu nhiên dài ở mọi môi trường.

## Chạy local không Docker

Tạo cấu hình SQLite riêng cho phát triển local rồi khởi tạo database bằng Alembic:

```powershell
cd backend
Copy-Item .env.example .env
python -m alembic upgrade head
```

SQLite chỉ phục vụ phát triển local và test; PostgreSQL vẫn là database production.

## PostgreSQL production hoặc staging

Yêu cầu PostgreSQL 16+ đang chạy tại `localhost:5432`. Tạo database và tài khoản phát triển bằng `psql`:

```powershell
psql -U postgres -c "CREATE USER chushop WITH PASSWORD 'chushop';"
psql -U postgres -c "CREATE DATABASE chushop OWNER chushop;"
```

Sau khi tạo database, cập nhật `DATABASE_URL` và `SECRET_KEY` trong biến môi trường deployment hoặc `backend/.env`. Không dùng mật khẩu hay secret mẫu ở môi trường production.

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

API chạy tại `http://localhost:8000`; tài liệu OpenAPI tại `http://localhost:8000/docs`. Dùng `/health` để kiểm tra tiến trình và `/ready` để kiểm tra cả kết nối database. Access token Bearer hết hạn sau `ACCESS_TOKEN_EXPIRE_MINUTES` (mặc định 60 phút).

Kiểm tra backend:

```powershell
cd backend
python -m pytest -q
python -m ruff check --no-cache .
python -m ruff format --no-cache --check .
python -m alembic upgrade head --sql
```

## Frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend chạy tại `http://localhost:3000` và gọi API qua `NEXT_PUBLIC_API_URL`.

Kiểm tra frontend:

```powershell
cd frontend
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run build
```

## API M0-M5

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
POST /api/v1/businesses
GET  /api/v1/businesses
GET  /api/v1/businesses/{business_id}
POST /api/v1/businesses/{business_id}/products
GET  /api/v1/businesses/{business_id}/products
GET  /api/v1/businesses/{business_id}/products/{product_id}
PATCH /api/v1/businesses/{business_id}/products/{product_id}
DELETE /api/v1/businesses/{business_id}/products/{product_id}
POST /api/v1/businesses/{business_id}/sales/imports/preview
POST /api/v1/businesses/{business_id}/sales/imports
DELETE /api/v1/businesses/{business_id}/sales/imports/{import_id}
POST /api/v1/businesses/{business_id}/sales/orders
GET  /api/v1/businesses/{business_id}/sales/orders
DELETE /api/v1/businesses/{business_id}/sales/orders/{order_id}
POST /api/v1/businesses/{business_id}/expenses
GET  /api/v1/businesses/{business_id}/expenses
PATCH /api/v1/businesses/{business_id}/expenses/{expense_id}
DELETE /api/v1/businesses/{business_id}/expenses/{expense_id}
GET  /api/v1/businesses/{business_id}/analytics/summary
POST /api/v1/businesses/{business_id}/assistant/conversations
GET  /api/v1/businesses/{business_id}/assistant/conversations
GET  /api/v1/businesses/{business_id}/assistant/conversations/{conversation_id}
POST /api/v1/businesses/{business_id}/assistant/conversations/{conversation_id}/messages
GET  /api/v1/admin/users
PATCH /api/v1/admin/users/{user_id}/status
GET  /api/v1/admin/businesses
GET  /api/v1/admin/audit-logs
```

Endpoint analytics nhận `date_from` và `date_to` theo định dạng `YYYY-MM-DD`. Tin nhắn gửi trợ lý có thể nhận cùng khoảng ngày; nếu bỏ trống, backend dùng từ đầu tháng hiện tại đến hôm nay theo múi giờ doanh nghiệp. Công thức được mô tả tại `docs/product/financial-metrics.md`, giới hạn trợ lý tại `docs/product/ai-assistant.md`, và định dạng CSV/XLSX tại `docs/product/sales-import.md`.

Mọi API doanh nghiệp đều yêu cầu Bearer token và chỉ trả dữ liệu nơi người dùng có `BusinessMember`.

## Platform Admin

Quyền quản trị hệ thống tách biệt với vai trò OWNER/MANAGER/MEMBER trong doanh nghiệp. Hãy đăng ký tài khoản bình thường trước, sau đó cấp quyền bằng lệnh vận hành:

```powershell
cd backend
python -m app.cli.platform_admin --email admin@example.com
```

Thu hồi quyền bằng cùng lệnh với cờ `--revoke`. Không có tài khoản hoặc mật khẩu admin mặc định. Xem quy trình và giới hạn tại `docs/operations/platform-admin.md`.

## Cấu hình Trợ lý AI (LLM Provider)

Trợ lý AI hỗ trợ cả **Mock Provider** (local deterministic cho kiểm thử) và **Real LLM Provider** (OpenAI / Gemini / Groq...):

- `LLM_PROVIDER`: `mock` (mặc định) hoặc `openai`
- `LLM_API_KEY`: API Key của nhà cung cấp LLM
- `LLM_MODEL`: Tên model (ví dụ: `gpt-4o-mini`, `gemini-1.5-flash`)
- `LLM_BASE_URL`: URL API tùy chỉnh (mặc định `https://api.openai.com/v1`)
