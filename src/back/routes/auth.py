from fastapi import APIRouter, Depends, Response, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from controllers.login import LoginController
from schemas.auth import LoginSchema, TokenResponse, LogoutResponse, UserInfoResponse
from middleware.auth_middleware import get_current_user, get_current_user_id

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(credentials: LoginSchema, response: Response, db: Session = Depends(get_db)):
    """
    Authentifie un utilisateur et retourne les tokens

    Les tokens sont également stockés dans des cookies httpOnly :
    - access_token : valide 15 minutes
    - refresh_token : valide 30 jours
    """
    result = LoginController.login(db, credentials.email, credentials.password)

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


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Génère un nouveau access token à partir du refresh token

    Le refresh token doit être présent dans les cookies
    """

    refresh_token_str = request.cookies.get("refresh_token")

    if not refresh_token_str:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Refresh token missing"},
        )

    result = LoginController.refresh_access_token(db, refresh_token_str)

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
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Déconnecte l'utilisateur et révoque les tokens
    """
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")

    if not access_token or not refresh_token:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Tokens missing"},
        )

    result = LoginController.logout(db, access_token, refresh_token)

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return result


@router.post(
    "/logout-all", response_model=LogoutResponse, status_code=status.HTTP_200_OK
)
def logout_all_devices(
    response: Response,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Déconnecte l'utilisateur de tous ses appareils
    (Nécessite d'être authentifié)
    """
    result = LoginController.logout_all_devices(db, user_id)

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return result


@router.get("/me", response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
def get_current_user_info(user=Depends(get_current_user)):
    """
    Retourne les informations de l'utilisateur connecté
    (Route protégée - nécessite un access token valide)
    """
    return {
        "id": user.idUser,
        "email": user.email,
        "username": user.username,
        "role": user.role.value,
        "banned": user.banned,
        "isVerified": user.isVerified,
    }
