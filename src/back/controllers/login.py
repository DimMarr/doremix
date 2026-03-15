import os
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from repositories import UserRepository, AccessTokenRepository, RefreshTokenRepository
from passlib.context import CryptContext


class LoginController:
    pwd_context = CryptContext(schemes=["bcrypt"])
    pepper = os.getenv("PEPPER_KEY")

    ACCESS_TOKEN_DURATION = 15
    REFRESH_TOKEN_DURATION = 43200

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str):
        if LoginController.pepper is None:
            raise HTTPException(
                status_code=500, detail="PEPPER_KEY is missing in .env file"
            )

        user = await UserRepository.get_by_email(db, email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if user.banned:
            raise HTTPException(status_code=403, detail="Your account has been banned")

        peppered_pw = password + LoginController.pepper
        pre_hashed_password = hashlib.sha256(peppered_pw.encode("utf-8")).hexdigest()

        if not LoginController.pwd_context.verify(pre_hashed_password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not user.isVerified:
            raise HTTPException(
                status_code=403, detail="Please verify your email before logging in"
            )

        access_token = await AccessTokenRepository.create_token(
            db=db,
            user_id=user.idUser,
            duration_minutes=LoginController.ACCESS_TOKEN_DURATION,
        )
        refresh_token = await RefreshTokenRepository.create_token(
            db=db,
            user_id=user.idUser,
            duration_minutes=LoginController.REFRESH_TOKEN_DURATION,
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
    async def check_access_token_validity(db: AsyncSession, access_token_str: str):
        access_token = await AccessTokenRepository.get_valid_token(db, access_token_str)
        if not access_token:
            raise HTTPException(
                status_code=401, detail="Invalid or expired access token"
            )
        return {
            "access_token": access_token_str,
            "validity": True,
        }

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token_str: str):
        refresh_token = await RefreshTokenRepository.get_valid_token(
            db, refresh_token_str
        )
        if not refresh_token:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )

        user = await UserRepository.get_user_by_id(db, refresh_token.idUser)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.banned:
            raise HTTPException(status_code=403, detail="Your account has been banned")

        access_token = await AccessTokenRepository.create_token(
            db=db,
            user_id=user.idUser,
            duration_minutes=LoginController.ACCESS_TOKEN_DURATION,
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
    async def logout(db: AsyncSession, access_token_str: str, refresh_token_str: str):
        try:
            await AccessTokenRepository.revoke_token(db, access_token_str)
            await RefreshTokenRepository.revoke_token(db, refresh_token_str)
            return {"message": "Successfully logged out"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error during logout: {str(e)}"
            )

    @staticmethod
    async def logout_all_devices(db: AsyncSession, user_id: int):
        try:
            await AccessTokenRepository.revoke_all_user_tokens(db, user_id)
            await RefreshTokenRepository.revoke_all_user_tokens(db, user_id)
            return {"message": "Successfully logged out from all devices"}
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error during logout: {str(e)}"
            )
