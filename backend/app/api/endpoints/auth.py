"""
Authentication endpoints.
"""

from fastapi import APIRouter, Request, Response, status
from fastapi.responses import JSONResponse

from app.api.deps import AuthServiceDep, ResetEmailDep
from app.core.config import settings
from app.core.limiter import limit
from app.models.domain.user import User
from app.models.schemas.password import (
    NewPassword,
    PasswordResetRequest,
    VerificationCode,
)
from app.models.schemas.token import Token, TokenToRefresh
from app.models.schemas.user import UserBase, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserBase, status_code=status.HTTP_201_CREATED)
@limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def register_user(
    user_in: UserRegister,
    request: Request,
    response: Response,
    auth_service: AuthServiceDep,
) -> User:
    """
    Register a new user in the system.
    """
    return await auth_service.register_user(user_in=user_in)


@router.post("/login", response_model=Token)
@limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def login(
    data: UserLogin,
    request: Request,
    response: Response,
    auth_service: AuthServiceDep,
) -> Token:
    """
    Login user to the system.
    """
    return await auth_service.login(
        username=data.username,
        password=data.password,
        response=response,
        fingerprint=data.fingerprint,
    )


@router.post("/refresh", response_model=Token)
async def refresh(
    body: TokenToRefresh,
    request: Request,
    response: Response,
    auth_service: AuthServiceDep,
) -> Token:
    """
    Refresh user authentication tokens.
    """
    return await auth_service.refresh_token(
        request=request,
        fingerprint=body.fingerprint,
        response=response,
    )


@router.get("/logout")
async def logout(
    request: Request,
    auth_service: AuthServiceDep,
) -> Response:
    """
    Logout user from the system.
    """
    return await auth_service.logout(request=request)


@router.post("/reset-password")
@limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def reset_password(
    request_data: PasswordResetRequest,
    request: Request,
    response: Response,
    auth_service: AuthServiceDep,
) -> JSONResponse:
    """
    Initiates password reset.
    """
    return await auth_service.request_reset_password(request_data.email, request)


@router.post("/verify-code")
async def verify_code(
    code_data: VerificationCode,
    request: Request,
    response: Response,
    auth_service: AuthServiceDep,
    email: ResetEmailDep,
) -> JSONResponse:
    """
    Verifies confirmation code for password reset.
    """
    return await auth_service.verify_code(email, code_data.code, request)


@router.post("/new-password")
async def set_new_password(
    password_data: NewPassword,
    request: Request,
    response: Response,
    auth_service: AuthServiceDep,
    email: ResetEmailDep,
) -> JSONResponse:
    """
    Sets new user password.
    """
    return await auth_service.set_new_password(
        email,
        password_data.new_password,
        password_data.confirm_new_password,
        request,
    )
