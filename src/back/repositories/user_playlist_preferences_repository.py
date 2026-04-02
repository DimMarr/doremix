from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user_playlist_preferences import UserPlaylistPreferences
from typing import Optional, List


class UserPlaylistPreferencesRepository:
    @staticmethod
    async def get(db: AsyncSession, user_id: int) -> UserPlaylistPreferences | None:
        result = await db.execute(
            select(UserPlaylistPreferences).filter(
                UserPlaylistPreferences.idUser == user_id
            )
        )
        return result.scalars().first() or None

    @staticmethod
    async def upsert(
        db: AsyncSession,
        user_id: int,
        sort_mode: str,
        custom_order: Optional[List[int]],
    ) -> UserPlaylistPreferences:
        result = await db.execute(
            select(UserPlaylistPreferences).filter(
                UserPlaylistPreferences.idUser == user_id
            )
        )
        prefs: UserPlaylistPreferences | None = result.scalars().first()
        if prefs is None:
            prefs = UserPlaylistPreferences(idUser=user_id)
            db.add(prefs)
        prefs.sort_mode = sort_mode
        prefs.custom_order = custom_order
        await db.commit()
        await db.refresh(prefs)
        return prefs
