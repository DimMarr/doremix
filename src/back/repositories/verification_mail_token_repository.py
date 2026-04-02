import os
import random
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models import VerificationMailToken, User


class VerificationMailTokenRepository:
    @staticmethod
    def hash_code(code: str) -> str:
        secret_key = os.getenv("TOKEN_MAIL_SECRET_KEY")
        if not secret_key:
            raise ValueError("TOKEN_MAIL_SECRET_KEY is missing in .env file")
        return hashlib.sha256((code + secret_key).encode("utf-8")).hexdigest()

    @staticmethod
    async def create_mail_verif_token(db: AsyncSession, user_id: int) -> str:
        # Supprime les anciens codes de cet utilisateur
        await db.execute(
            delete(VerificationMailToken).where(VerificationMailToken.idUser == user_id)
        )

        raw_code = str(random.randint(100000, 999999))
        hashed_code = VerificationMailTokenRepository.hash_code(raw_code)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        db_token = VerificationMailToken(
            token=hashed_code, idUser=user_id, expiresAt=expires_at
        )
        db.add(db_token)
        await db.commit()

        return raw_code  # on retourne le code en clair pour l'envoyer par mail

    @staticmethod
    async def verify_code(db: AsyncSession, user_id: int, raw_code: str):
        hashed_code = VerificationMailTokenRepository.hash_code(raw_code)

        result = await db.execute(
            select(VerificationMailToken).where(
                VerificationMailToken.idUser == user_id,
                VerificationMailToken.token == hashed_code,
            )
        )
        token_obj = result.scalars().first()

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
    async def confirm_email(db: AsyncSession, email: str, raw_code: str):
        user = await db.execute(select(User).where(User.email == email))
        user = user.scalars().first()

        if not user:
            return "invalid"

        if user.isVerified:
            return "already_verified"

        result = await VerificationMailTokenRepository.verify_code(
            db, user.idUser, raw_code
        )

        if result == "invalid":
            return "invalid"
        if result == "expired":
            return "expired"

        user.isVerified = True
        await db.execute(
            delete(VerificationMailToken).where(
                VerificationMailToken.idUser == user.idUser
            )
        )
        await db.commit()
        return "verified"

    @staticmethod
    async def resend_code(db: AsyncSession, email: str) -> str | None:
        user_result = await db.execute(select(User).where(User.email == email))
        user = user_result.scalars().first()

        if not user or user.isVerified:
            return None

        raw_code = await VerificationMailTokenRepository.create_mail_verif_token(
            db, user.idUser
        )
        return raw_code

    @staticmethod
    async def revoke_all_user_tokens(db: AsyncSession, user_id: int):
        await db.execute(
            delete(VerificationMailToken).where(VerificationMailToken.idUser == user_id)
        )
        await db.commit()
