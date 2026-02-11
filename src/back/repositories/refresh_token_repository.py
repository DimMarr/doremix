import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from back.models.acces_token import Token, TokenTypes
from typing import cast


class RefreshTokenRepository:
    @staticmethod
    def hash_token(cookieToken: str) -> str:
        secret_key = os.getenv("TOKEN_SECRET_KEY")
        if not secret_key:
            raise ValueError("TOKEN_SECRET_KEY is missing in .env file")

        combined = cookieToken + secret_key
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    @staticmethod
    def create_token(
        db: Session, userId: int, token_type: TokenTypes, durationMinutes: int
    ) -> Token:
        cookieToken = secrets.token_urlsafe(64)  # not stored in DB
        hashedToken = RefreshTokenRepository.hash_token(cookieToken)
        expiresAt = datetime.now(timezone.utc) + timedelta(minutes=durationMinutes)

        dbToken = Token(
            token=hashedToken, type=token_type, idUser=userId, expiresAt=expiresAt
        )

        db.add(dbToken)
        db.commit()
        db.refresh(dbToken)

        # we return the unhashed token to use it in cookies
        dbToken.token = cookieToken
        return dbToken

    @staticmethod
    def get_valid_token(
        db: Session, cookieTokenStr: str, required_type: TokenTypes
    ) -> Token | None:
        hashedTokenToCheck = RefreshTokenRepository.hash_token(cookieTokenStr)

        result = (
            db.query(Token)
            .filter(
                Token.token == hashedTokenToCheck,
                Token.type == required_type,
                Token.expiresAt > datetime.now(timezone.utc),
            )
            .first()
        )
        return cast(Token, result) if result else None

    @staticmethod
    def revoke_token(db: Session, cookieTokenStr: str):
        hashedToken = RefreshTokenRepository.hash_token(cookieTokenStr)
        db.query(Token).filter(Token.token == hashedToken).delete()
        db.commit()

    @staticmethod
    def revoke_all_user_tokens(db: Session, userId: int):
        db.query(Token).filter(Token.idUser == userId).delete()
        db.commit()

    @staticmethod
    def clean_expired_tokens(db: Session):
        now = datetime.now(timezone.utc)
        db.query(Token).filter(Token.expiresAt < now).delete()
        db.commit()
