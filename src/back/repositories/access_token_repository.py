import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from models.acces_token import AccessToken
from typing import cast


class AccessTokenRepository:
    @staticmethod
    def hash_token(cookieToken: str) -> str:
        secret_key = os.getenv("TOKEN_SECRET_KEY")
        if not secret_key:
            raise ValueError("TOKEN_SECRET_KEY is missing in .env file")

        combined = cookieToken + secret_key
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    @staticmethod
    def create_token(db: Session, userId: int, durationMinutes: int) -> AccessToken:
        cookieToken = secrets.token_urlsafe(64)  # not stored in DB
        hashedToken = AccessTokenRepository.hash_token(cookieToken)
        expiresAt = datetime.now(timezone.utc) + timedelta(minutes=durationMinutes)

        dbToken = AccessToken(token=hashedToken, idUser=userId, expiresAt=expiresAt)

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
    ) -> AccessToken | None:
        hashedTokenToCheck = AccessTokenRepository.hash_token(cookieTokenStr)

        result = (
            db.query(AccessToken)
            .filter(
                AccessToken.token == hashedTokenToCheck,
                AccessToken.expiresAt > datetime.now(timezone.utc),
            )
            .first()
        )
        return cast(AccessToken, result) if result else None

    @staticmethod
    def revoke_token(db: Session, cookieTokenStr: str):
        hashedToken = AccessTokenRepository.hash_token(cookieTokenStr)
        db.query(AccessToken).filter(AccessToken.token == hashedToken).delete()
        db.commit()

    @staticmethod
    def revoke_all_user_tokens(db: Session, userId: int):
        db.query(AccessToken).filter(AccessToken.idUser == userId).delete()
        db.commit()

    @staticmethod
    def clean_expired_tokens(db: Session):
        now = datetime.now(timezone.utc)
        db.query(AccessToken).filter(AccessToken.expiresAt < now).delete()
        db.commit()
