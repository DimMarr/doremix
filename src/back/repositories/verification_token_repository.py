import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from back.models.verification_token import RefreshToken
from typing import cast


class VerificationTokenRepository:
    @staticmethod
    def hash_token(cookieToken: str) -> str:
        secret_key = os.getenv("TOKEN_SECRET_KEY")
        if not secret_key:
            raise ValueError("TOKEN_SECRET_KEY is missing in .env file")

        combined = cookieToken + secret_key
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    @staticmethod
    def create_token(db: Session, userId: int, durationMinutes: int) -> VerificationToken:
        cookieToken = secrets.token_urlsafe(64)  # not stored in DB
        hashedToken = VerificationTokenRepository.hash_token(cookieToken)
        expiresAt = datetime.now(timezone.utc) + timedelta(minutes=durationMinutes)

        dbToken = VerificationToken(token=hashedToken, idUser=userId, expiresAt=expiresAt)

        db.add(dbToken)
        db.commit()
        db.refresh(dbToken)

        # we return the unhashed token to use it in cookies
        dbToken.token = cookieToken
        return dbToken

    @staticmethod
    def get_valid_token(
        db: Session,
        cookieTokenStr: str,
    ) -> VerificationToken | None:
        hashedTokenToCheck = VerificationTokenRepository.hash_token(cookieTokenStr)

        result = (
            db.query(VerificationToken)
            .filter(
                VerificationToken.token == hashedTokenToCheck,
                VerificationToken.expiresAt > datetime.now(timezone.utc),
            )
            .first()
        )
        return cast(VerificationToken, result) if result else None

    @staticmethod
    def revoke_token(db: Session, cookieTokenStr: str):
        hashedToken = VerificationTokenRepository.hash_token(cookieTokenStr)
        db.query(VerificationToken).filter(VerificationToken.token == hashedToken).delete()
        db.commit()

    @staticmethod
    def revoke_all_user_tokens(db: Session, userId: int):
        db.query(VerificationToken).filter(VerificationToken.idUser == userId).delete()
        db.commit()

    @staticmethod
    def clean_expired_tokens(db: Session):
        now = datetime.now(timezone.utc)
        db.query(VerificationToken).filter(VerificationToken.expiresAt < now).delete()
        db.commit()
