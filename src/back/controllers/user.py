from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from repositories import UserRepository


class UserController:
    @staticmethod
    async def get_all_users(db: AsyncSession):
        users = await UserRepository.get_all(db)
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        return users

    @staticmethod
    async def get_user(db: AsyncSession, idUser: int):
        user = await UserRepository.get_by_id(db, idUser)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
