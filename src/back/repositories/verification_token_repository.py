import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models.verification_token import VerificationToken
from typing import cast


class VerificationTokenRepository:
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
    ) -> VerificationToken:
        cookie_token = secrets.token_urlsafe(64)  # not stored in DB
        hashed_token = VerificationTokenRepository.hash_token(cookie_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)
        db_token = VerificationToken(
            token=hashed_token, idUser=user_id, expiresAt=expires_at
        )
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        # we return the unhashed token to use it in cookies
        db_token.token = cookie_token
        return db_token

    @staticmethod
    async def get_valid_token(
        db: AsyncSession, cookie_token_str: str
    ) -> VerificationToken | None:
        hashed_token = VerificationTokenRepository.hash_token(cookie_token_str)
        result = await db.execute(
            select(VerificationToken).filter(
                VerificationToken.token == hashed_token,
                VerificationToken.expiresAt > datetime.now(timezone.utc),
            )
        )
        token = result.scalars().first()
        return cast(VerificationToken, token) if token else None

    @staticmethod
    async def revoke_token(db: AsyncSession, cookie_token_str: str) -> None:
        hashed_token = VerificationTokenRepository.hash_token(cookie_token_str)
        await db.execute(
            delete(VerificationToken).filter(VerificationToken.token == hashed_token)
        )
        await db.commit()

    @staticmethod
    async def revoke_all_user_tokens(db: AsyncSession, user_id: int) -> None:
        await db.execute(
            delete(VerificationToken).filter(VerificationToken.idUser == user_id)
        )
        await db.commit()

    @staticmethod
    async def clean_expired_tokens(db: AsyncSession) -> None:
        now = datetime.now(timezone.utc)
        await db.execute(
            delete(VerificationToken).filter(VerificationToken.expiresAt < now)
        )
        await db.commit()
