from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, noload
from sqlalchemy import select
from models import User
from typing import Optional, List

class UserRepository:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[User]:
        result = await db.execute(
            select(User).options(noload(User.playlists))
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(
            select(User).where(User.idUser == user_id).options(selectinload(User.playlists))
        )
        return result.scalars().first()
