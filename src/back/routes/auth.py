from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers.auth_controller import AuthController
from schemas.auth import SignupRequest, LoginRequest, TokenResponse, UserResponse
from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    summary="Create a new account",
    description="Register a new user with University of Montpellier email address.",
)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    result = AuthController.signup(
        db, request.email, request.password, request.username
    )
    return result


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login to account",
    description="Authenticate user and receive JWT token.",
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    result = AuthController.login(db, request.email, request.password)
    return result


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get authenticated user information from JWT token.",
)
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "idUser": current_user.idUser,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role.value,
        "banned": current_user.banned,
    }
