import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models import VerificationMailToken, User


class VerificationMailTokenRepository:
    @staticmethod
    def hash_token(token: str) -> str:
        secret_key = os.getenv("TOKEN_MAIL_SECRET_KEY")
        if not secret_key:
            raise ValueError("TOKEN_MAIL_SECRET_KEY is missing in .env file")
        return hashlib.sha256((token + secret_key).encode("utf-8")).hexdigest()

    @staticmethod
    async def create_mail_verif_token(
        db: AsyncSession, user_id: int
    ) -> VerificationMailToken:
        raw_token = secrets.token_urlsafe(64)
        hashed_token = VerificationMailTokenRepository.hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        db_token = VerificationMailToken(
            token=hashed_token, idUser=user_id, expiresAt=expires_at
        )

        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)

        db_token.token = raw_token

        return db_token

    @staticmethod
    async def get_token_even_expired(db: AsyncSession, raw_token: str):
        hashed = VerificationMailTokenRepository.hash_token(raw_token)

        result = await db.execute(
            select(VerificationMailToken).where(VerificationMailToken.token == hashed)
        )
        return result.scalars().first()

    @staticmethod
    async def verify_token(db: AsyncSession, raw_token: str):
        token_obj = await VerificationMailTokenRepository.get_token_even_expired(
            db, raw_token
        )

        if not token_obj:
            return "invalid"

        now = datetime.now(timezone.utc)
        expires = token_obj.expiresAt

        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        if now > expires:
            return "expired"

        return token_obj

    @staticmethod
    async def confirm_email(db: AsyncSession, raw_token: str):
        result = await VerificationMailTokenRepository.verify_token(db, raw_token)

        if result == "invalid":
            return "invalid"

        if result == "expired":
            return "expired"

        token_obj = result

        user = await db.get(User, token_obj.idUser)

        if not user:
            return "invalid"

        if user.isVerified:
            return "already_verified"

        user.isVerified = True

        await db.execute(
            delete(VerificationMailToken).where(
                VerificationMailToken.idUser == user.idUser
            )
        )

        await db.commit()

        return "verified"

    @staticmethod
    async def revoke_all_user_tokens(db: AsyncSession, user_id: int):
        await db.execute(
            delete(VerificationMailToken).where(VerificationMailToken.idUser == user_id)
        )
        await db.commit()
