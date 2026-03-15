import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models.refresh_token import RefreshToken
from typing import cast


class RefreshTokenRepository:
    @staticmethod
    def hash_token(cookie_token: str) -> str:
        secret_key = os.getenv("TOKEN_SECRET_KEY")
        if not secret_key:
            raise ValueError("TOKEN_SECRET_KEY is missing in .env file")
        combined = cookie_token + secret_key
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    @staticmethod
    async def create_token(
        db: AsyncSession, user_id: int, duration_minutes: int
    ) -> str:
        cookie_token = secrets.token_urlsafe(64)  # not stored in DB
        hashed_token = RefreshTokenRepository.hash_token(cookie_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        db_token = RefreshToken(
            token=hashed_token, idUser=user_id, expiresAt=expires_at
        )
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        # we return the unhashed token to use it in cookies
        return cookie_token

    @staticmethod
    async def get_valid_token(
        db: AsyncSession, cookie_token_str: str
    ) -> RefreshToken | None:
        hashed_token = RefreshTokenRepository.hash_token(cookie_token_str)
        result = await db.execute(
            select(RefreshToken).filter(
                RefreshToken.token == hashed_token,
                RefreshToken.expiresAt > datetime.now(timezone.utc),
            )
        )
        token = result.scalars().first()
        return cast(RefreshToken, token) if token else None

    @staticmethod
    async def revoke_token(
        db: AsyncSession, cookie_token_str: str, commit: bool = True
    ) -> None:
        hashed_token = RefreshTokenRepository.hash_token(cookie_token_str)
        await db.execute(
            delete(RefreshToken).filter(RefreshToken.token == hashed_token)
        )
        if commit:
            await db.commit()

    @staticmethod
    async def revoke_all_user_tokens(
        db: AsyncSession, user_id: int, commit: bool = True
    ) -> None:
        await db.execute(delete(RefreshToken).filter(RefreshToken.idUser == user_id))
        if commit:
            await db.commit()

    @staticmethod
    async def clean_expired_tokens(db: AsyncSession) -> None:
        now = datetime.now(timezone.utc)
        await db.execute(delete(RefreshToken).filter(RefreshToken.expiresAt < now))
        await db.commit()
