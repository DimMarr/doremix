from typing import Optional, List, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result

from models import User


class UserRepository:
    @staticmethod
    async def get_all(db: AsyncSession) -> List[User]:
        result: Result[tuple[User]] = await db.execute(
            select(User).order_by(User.idUser)
        )
        return cast(List[User], result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, idUser: int) -> Optional[User]:
        result: Result[tuple[User]] = await db.execute(
            select(User).where(User.idUser == idUser)
        )
        return cast(Optional[User], result.scalars().first())
