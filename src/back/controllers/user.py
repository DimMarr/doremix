from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from repositories import UserRepository


class UserController:
    @staticmethod
    async def get_all_users(db: AsyncSession):
        return await UserRepository.get_all(db)

    @staticmethod
    async def get_user(db: AsyncSession, idUser: int):
        return await UserRepository.get_by_id(db, idUser)

    @staticmethod
    async def get_user_playlists(db: AsyncSession, idUser: int):
        user = await UserRepository.get_by_id(db, idUser)
        if user:
            return user.playlists
        return []

