import os
import hashlib
from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories.user_repository import UserRepository
from repositories.access_token_repository import AccessTokenRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from passlib.context import CryptContext


class LoginController:
    pwd_context = CryptContext(schemes=["bcrypt"])
    pepper = os.getenv("PEPPER_KEY")

    ACCESS_TOKEN_DURATION = 15
    REFRESH_TOKEN_DURATION = 43200

    @staticmethod
    def login(db: Session, email: str, password: str):
        """
        Authentifie un utilisateur et génère les tokens d'accès et de rafraîchissement
        """
        if LoginController.pepper is None:
            raise HTTPException(
                status_code=500, detail="PEPPER_KEY is missing in .env file"
            )

        user = UserRepository.get_by_email(db, email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if user.banned:
            raise HTTPException(status_code=403, detail="Your account has been banned")

        if not user.isVerified:
            raise HTTPException(
                status_code=403, detail="Please verify your email before logging in"
            )

        peppered_pw = password + LoginController.pepper
        pre_hashed_password = hashlib.sha256(peppered_pw.encode("utf-8")).hexdigest()

        if not LoginController.pwd_context.verify(pre_hashed_password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = AccessTokenRepository.create_token(
            db=db,
            userId=user.idUser,
            durationMinutes=LoginController.ACCESS_TOKEN_DURATION,
        )

        refresh_token = RefreshTokenRepository.create_token(
            db=db,
            userId=user.idUser,
            durationMinutes=LoginController.REFRESH_TOKEN_DURATION,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.idUser,
                "email": user.email,
                "username": user.username,
                "role": user.role.value,
                "banned": user.banned,
                "isVerified": user.isVerified,
            },
        }

    @staticmethod
    def check_access_token_validity(db: Session, access_token_str: str):
        access_token = AccessTokenRepository.get_valid_token(db, access_token_str)

        if not access_token:
            raise HTTPException(
                status_code=401, detail="Invalid or expired access token"
            )

        return {
            "access_token": access_token_str,
            "validity": True,
        }

    @staticmethod
    def refresh_access_token(db: Session, refresh_token_str: str):
        """
        Génère un nouveau access token à partir d'un refresh token valide
        """
        refresh_token = RefreshTokenRepository.get_valid_token(db, refresh_token_str)

        if not refresh_token:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )

        user = UserRepository.get_user_by_id(db, refresh_token.idUser)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.banned:
            raise HTTPException(status_code=403, detail="Your account has been banned")

        access_token = AccessTokenRepository.create_token(
            db=db,
            userId=user.idUser,
            durationMinutes=LoginController.ACCESS_TOKEN_DURATION,
        )

        return {
            "access_token": access_token,
            "user": {
                "id": user.idUser,
                "email": user.email,
                "username": user.username,
                "role": user.role.value,
                "banned": user.banned,
                "isVerified": user.isVerified,
            },
        }

    @staticmethod
    def logout(db: Session, access_token_str: str, refresh_token_str: str):
        """
        Révoque les tokens de l'utilisateur (logout)
        """
        try:
            AccessTokenRepository.revoke_token(db, access_token_str)
            RefreshTokenRepository.revoke_token(db, refresh_token_str)

            return {"message": "Successfully logged out"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error during logout: {str(e)}"
            )

    @staticmethod
    def logout_all_devices(db: Session, user_id: int):
        """
        Révoque tous les tokens d'un utilisateur (déconnexion de tous les appareils)
        """
        try:
            AccessTokenRepository.revoke_all_user_tokens(db, user_id)
            RefreshTokenRepository.revoke_all_user_tokens(db, user_id)

            return {"message": "Successfully logged out from all devices"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error during logout: {str(e)}"
            )
