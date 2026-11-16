from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.schema import LoginRequest, RegisterRequest, TokenResponse
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


def normalize_email(email: str) -> str:
    return email.strip().lower()


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: RegisterRequest) -> User:
        email = normalize_email(str(payload.email))
        if self.users.get_by_email(email) is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email đã tồn tại")
        try:
            user = self.users.add(
                email=email,
                password_hash=hash_password(payload.password),
                full_name=payload.full_name.strip(),
            )
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email đã tồn tại"
            ) from None
        return user

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.users.get_by_email(normalize_email(str(payload.email)))
        if (
            user is None
            or not user.is_active
            or not verify_password(payload.password, user.password_hash)
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không đúng",
            )
        settings = get_settings()
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            expires_in=settings.access_token_expire_minutes * 60,
            user=user,
        )
