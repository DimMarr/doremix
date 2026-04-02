from fastapi import APIRouter, Depends, Response, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from controllers.login import LoginController
from schemas.auth import (
    LoginSchema,
    AccessTokenValidity,
    TokenResponse,
    LogoutResponse,
    UserInfoResponse,
)
from middleware.auth_middleware import get_current_user, get_current_user_id
from pydantic import BaseModel


class VerifyEmailSchema(BaseModel):
    email: str
    code: str


class ResendVerificationSchema(BaseModel):
    email: str


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginSchema, response: Response, db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user and returns tokens.

    Tokens are also stored in httpOnly cookies:
    - access_token: valid for 15 minutes
    - refresh_token: valid for 30 days
    """
    result = await LoginController.login(db, credentials.email, credentials.password)

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=15 * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,
    )

    return result


@router.post(
    "/check-token", response_model=AccessTokenValidity, status_code=status.HTTP_200_OK
)
async def check_token(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Checks the validity of the current access token.
    """
    access_token_str = request.cookies.get("access_token")
    return await LoginController.check_access_token_validity(db, access_token_str)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    """
    Generates a new access token from the refresh token.

    The refresh token must be present in the cookies.
    """
    refresh_token_str = request.cookies.get("refresh_token")

    if not refresh_token_str:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Refresh token missing"},
        )

    result = await LoginController.refresh_access_token(db, refresh_token_str)

    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=15 * 60,
    )

    return result


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    """
    Logs out the user and revokes their tokens.
    """
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token or not refresh_token:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Tokens missing"},
        )

    result = await LoginController.logout(db, access_token, refresh_token)

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return result


@router.post(
    "/logout-all", response_model=LogoutResponse, status_code=status.HTTP_200_OK
)
async def logout_all_devices(
    response: Response,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Logs out the user from all devices.
    (Requires authentication)
    """
    result = await LoginController.logout_all_devices(db, user_id)

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return result


@router.get("/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(user=Depends(get_current_user)):
    """
    Returns the current authenticated user's information.
    (Protected route - requires a valid access token)
    """
    return {
        "id": user.idUser,
        "email": user.email,
        "username": user.username,
        "role": user.role.value,
        "banned": user.banned,
        "isVerified": user.isVerified,
    }


@router.post("/verify-email")
async def verify_email(data: VerifyEmailSchema, db: AsyncSession = Depends(get_db)):
    return await LoginController.confirm_email(db, data.email, data.code)


@router.post("/resend-verification-email")
async def resend_verification_email(
    data: ResendVerificationSchema, db: AsyncSession = Depends(get_db)
):
    return await LoginController.resend_verification_email(db, data.email)
