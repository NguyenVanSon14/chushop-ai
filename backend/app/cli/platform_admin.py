import argparse

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.auth.service import normalize_email
from app.modules.users.repository import UserRepository


def set_platform_admin(db: Session, *, email: str, enabled: bool) -> bool:
    user = UserRepository(db).get_by_email(normalize_email(email))
    if user is None:
        return False
    user.is_platform_admin = enabled
    db.commit()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Grant or revoke ChủShop AI platform admin")
    parser.add_argument("--email", required=True, help="Email of an existing account")
    parser.add_argument(
        "--revoke", action="store_true", help="Revoke access instead of granting it"
    )
    args = parser.parse_args()

    with SessionLocal() as db:
        enabled = not args.revoke
        if not set_platform_admin(db, email=args.email, enabled=enabled):
            parser.error("Không tìm thấy tài khoản với email này")

    state = "đã được cấp" if enabled else "đã bị thu hồi"
    print(f"Quyền platform admin {state} cho {normalize_email(args.email)}")


if __name__ == "__main__":
    main()
