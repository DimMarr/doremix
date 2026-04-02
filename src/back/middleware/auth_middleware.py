from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from repositories.access_token_repository import AccessTokenRepository
from repositories.user_repository import UserRepository
from database import AsyncSessionLocal


class AuthMiddleware:
    """
    Middleware to verify the access token in cookies
    and attach the user to the request.
    """

    @staticmethod
    async def verify_access_token(request: Request, call_next):
        """
        Verifies the access token for all protected routes.
        """
        public_routes = [
            "/auth/register",
            "/auth/login",
            "/auth/refresh",
            "/auth/verify-email",
            "/auth/resend-verification-email",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

        if request.method == "OPTIONS":
            return await call_next(request)

        if any(request.url.path.startswith(route) for route in public_routes):
            return await call_next(request)

        access_token = request.cookies.get("access_token")
        if not access_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Access token missing"},
            )

        async with AsyncSessionLocal() as db:
            try:
                db_token = await AccessTokenRepository.get_valid_token(db, access_token)
                if not db_token:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Invalid or expired access token"},
                    )

                user = await UserRepository.get_user_by_id(db, db_token.idUser)
                if not user:
                    return JSONResponse(
                        status_code=status.HTTP_404_NOT_FOUND,
                        content={"detail": "User not found"},
                    )

                if user.banned:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": "Your account has been banned"},
                    )

                request.state.user = user
                request.state.user_id = user.idUser

            except Exception as e:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": f"Authentication error: {str(e)}"},
                )

        return await call_next(request)


def get_current_user(request: Request):
    """
    FastAPI dependency to get the authenticated user.
    Usage: user = Depends(get_current_user)
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return request.state.user


def get_current_user_id(request: Request) -> int:
    """
    FastAPI dependency to get the authenticated user's ID.
    """
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return int(request.state.user_id)


def require_role(allowed_roles: list[str]):
    """
    Dependency to verify the user's role.
    Usage: Depends(require_role(["ADMIN", "MODERATOR"]))
    """

    def role_checker(request: Request):
        user = get_current_user(request)
        if user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(allowed_roles)}",
            )
        return user

    return role_checker
