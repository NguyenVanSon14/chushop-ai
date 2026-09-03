from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser, DbSession
from app.modules.auth.schema import LoginRequest, RegisterRequest, TokenResponse
from app.modules.auth.service import AuthService
from app.modules.users.schema import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> UserRead:
    return UserRead.model_validate(AuthService(db).register(payload))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    return AuthService(db).login(payload)


@router.get("/me", response_model=UserRead)
def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
