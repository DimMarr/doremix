from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from controllers.register import RegisterController
from schemas.user import UserRegisterSchema

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description="Registers a user, hashes the password and generates a unique username.",
)
async def register(user_data: UserRegisterSchema, db: AsyncSession = Depends(get_db)):
    return await RegisterController.register(db, user_data)
