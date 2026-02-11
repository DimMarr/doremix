from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from controllers.register import RegisterController
from schemas.user import UserRegisterSchema

# /auth/register, /auth/login...
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau compte",
    description="Enregistre un utilisateur, hache le mot de passe et génère un username unique."
)
def register(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    return RegisterController.register(db, user_data)