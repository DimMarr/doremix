import os
import random
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from models import PasswordResetToken, User


class PasswordResetRepository:
    @staticmethod
    def hash_code(code: str) -> str:
        secret_key = os.getenv("TOKEN_MAIL_SECRET_KEY")
        if not secret_key:
            raise ValueError("TOKEN_MAIL_SECRET_KEY is missing in .env file")
        return hashlib.sha256((code + secret_key).encode("utf-8")).hexdigest()

    @staticmethod
    async def create_reset_code(db: AsyncSession, user_id: int) -> str:
        await db.execute(
            delete(PasswordResetToken).where(PasswordResetToken.idUser == user_id)
        )

        raw_code = str(random.randint(100000, 999999))
        hashed_code = PasswordResetRepository.hash_code(raw_code)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        db_token = PasswordResetToken(
            token=hashed_code, idUser=user_id, expiresAt=expires_at
        )
        db.add(db_token)
        await db.commit()

        return raw_code

    @staticmethod
    async def verify_code(db: AsyncSession, user_id: int, raw_code: str):
        hashed_code = PasswordResetRepository.hash_code(raw_code)

        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.idUser == user_id,
                PasswordResetToken.token == hashed_code,
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
    async def confirm_reset(
        db: AsyncSession, email: str, raw_code: str, new_password: str
    ):
        user = await db.execute(select(User).where(User.email == email))
        user = user.scalars().first()

        if not user:
            return "invalid"

        result = await PasswordResetRepository.verify_code(db, user.idUser, raw_code)

        if result == "invalid":
            return "invalid"
        if result == "expired":
            return "expired"

        import os
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"])
        pepper = os.getenv("PEPPER_KEY")
        if not pepper:
            return "error"

        import hashlib

        peppered_pw = new_password + pepper
        pre_hashed_password = hashlib.sha256(peppered_pw.encode("utf-8")).hexdigest()
        hashed_pw = pwd_context.hash(pre_hashed_password)

        user.password = hashed_pw
        await db.execute(
            delete(PasswordResetToken).where(PasswordResetToken.idUser == user.idUser)
        )
        await db.commit()
        return "reset"

    @staticmethod
    async def request_reset(db: AsyncSession, email: str) -> str | None:
        user_result = await db.execute(select(User).where(User.email == email))
        user = user_result.scalars().first()

        if not user:
            return None

        raw_code = await PasswordResetRepository.create_reset_code(db, user.idUser)
        return raw_code

    @staticmethod
    async def revoke_all_user_tokens(db: AsyncSession, user_id: int):
        await db.execute(
            delete(PasswordResetToken).where(PasswordResetToken.idUser == user_id)
        )
        await db.commit()
