from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from models.user import User, UserRole


class UserRepository:
    ADMIN_ROLE_ID = 3  # hardcodé pour que les moderators ne puissent pas ban les admins

    @staticmethod
    async def create(db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_all(db: AsyncSession) -> list[User]:
        result = await db.execute(select(User))
        return list(result.scalars().all())

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).filter(User.idUser == user_id))
        return cast(User | None, result.scalars().first())

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).filter(User.email == email))
        return cast(User | None, result.scalars().first())

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).filter(User.username == username))
        return cast(User | None, result.scalars().first())

    @staticmethod
    async def create_user(
        db: AsyncSession,
        email: str,
        username: str,
        password_hash: str,
        is_verified: bool,
    ) -> User:
        db_user = User(
            email=email,
            username=username,
            password=password_hash,
            isVerified=is_verified,
            role=UserRole.USER,
            banned=False,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def mark_as_verified(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).filter(User.idUser == user_id))
        user = cast(User | None, result.scalars().first())
        if user:
            user.is_verified = True
            await db.commit()
            await db.refresh(user)
        return user

    @staticmethod
    async def search_users(db: AsyncSession, query: str, limit: int = 10) -> list[User]:
        result = await db.execute(
            select(User)
            .filter(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_role(
        db: AsyncSession, user_id: int, new_role: UserRole
    ) -> User | None:
        result = await db.execute(select(User).filter(User.idUser == user_id))
        user = cast(User | None, result.scalars().first())
        if user:
            user.role = new_role
            await db.commit()
            await db.refresh(user)
        return user

    @staticmethod
    async def get_non_admin_ban_candidates(
        db: AsyncSession, current_user_id: int
    ) -> list[User]:
        result = await db.execute(
            select(User)
            .filter(
                User.idUser != current_user_id,
                User.idRole != UserRepository.ADMIN_ROLE_ID,
                User.banned.is_(False),
            )
            .order_by(User.idUser.asc())
        )
        return list(result.scalars().all())
