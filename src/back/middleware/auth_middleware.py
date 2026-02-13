from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from repositories.access_token_repository import AccessTokenRepository
from repositories.user_repository import UserRepository
from database import SessionLocal


class AuthMiddleware:
    """
    Middleware pour vérifier l'access token dans les cookies
    et attacher l'utilisateur à la requête
    """

    @staticmethod
    async def verify_access_token(request: Request, call_next):
        """
        Vérifie l'access token pour toutes les routes protégées
        """
        public_routes = [
            "/api/auth/register",
            "/api/auth/login",
            "/api/auth/refresh",
            "/api/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

        if any(request.url.path.startswith(route) for route in public_routes):
            return await call_next(request)

        access_token = request.cookies.get("access_token")

        if not access_token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Access token missing"},
            )

        db: Session = SessionLocal()
        try:
            db_token = AccessTokenRepository.get_valid_token(db, access_token)

            if not db_token:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid or expired access token"},
                )

            user = UserRepository.get_user_by_id(db, db_token.idUser)

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
        finally:
            db.close()

        response = await call_next(request)
        return response


def get_current_user(request: Request):
    """
    Dépendance FastAPI pour récupérer l'utilisateur authentifié
    À utiliser dans les routes comme : user = Depends(get_current_user)
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return request.state.user


def get_current_user_id(request: Request) -> int:
    """
    Dépendance FastAPI pour récupérer l'ID de l'utilisateur authentifié
    """
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    user_id: int = request.state.user_id
    return user_id


def require_role(allowed_roles: list[str]):
    """
    Dépendance pour vérifier le rôle de l'utilisateur
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
