# Platform Admin

Platform admin dùng để quản lý vận hành ChủShop AI, độc lập với vai trò thành viên trong từng doanh nghiệp. Hệ thống không tạo sẵn tài khoản hay mật khẩu admin.

## Cấp quyền đầu tiên

1. Đăng ký một tài khoản qua giao diện bình thường.
2. Chạy migration mới nhất.
3. Cấp quyền theo email đã đăng ký:

```powershell
cd backend
python -m alembic upgrade head
python -m app.cli.platform_admin --email admin@example.com
```

Đăng nhập lại hoặc tải lại trang. Liên kết **Quản trị hệ thống** sẽ xuất hiện và trang quản trị nằm tại `/admin`.

## Thu hồi quyền

```powershell
cd backend
python -m app.cli.platform_admin --email admin@example.com --revoke
```

## Nguyên tắc an toàn

- Người dùng thường nhận `403` khi gọi API admin.
- Admin không thể tự khóa tài khoản đang sử dụng.
- Tài khoản bị khóa không thể đăng nhập và token cũ cũng bị từ chối.
- Thao tác đổi trạng thái tài khoản được lưu trong `admin_audit_logs`.
- Việc cấp hoặc thu hồi platform admin chỉ thực hiện qua lệnh vận hành có quyền truy cập database; API không cho tự nâng quyền.
