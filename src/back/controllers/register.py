import os
import random
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from schemas import UserRegisterSchema
from repositories import UserRepository, VerificationMailTokenRepository
from passlib.context import CryptContext
from utils.email_sender import EmailSender

# TODO: Décommenter ces imports quand la vérification email sera active
# from repositories.verification_token_repository import VerificationTokenRepository
# from utils.email_verification import EmailVerification


class RegisterController:
    pwd_context = CryptContext(schemes=["bcrypt"])
    pepper = os.getenv("PEPPER_KEY")
    web_url = os.getenv("WEB_BASE_URL")

    @staticmethod
    async def register(db: AsyncSession, user_data: UserRegisterSchema):
        if RegisterController.pepper is None:
            raise HTTPException(
                status_code=500, detail="PEPPER_KEY is missing in .env file"
            )

        # 1. Vérification des données
        user = await UserRepository.get_by_email(db, user_data.email)
        if user:
            raise HTTPException(status_code=409, detail="This account already exists")

        peppered_pw = user_data.password + RegisterController.pepper
        pre_hashed_password = hashlib.sha256(peppered_pw.encode("utf-8")).hexdigest()
        hashed_pw = RegisterController.pwd_context.hash(pre_hashed_password)

        username = user_data.email.split("@")[0]
        while await UserRepository.get_by_username(db, username):
            random_suffix = random.randint(1000, 9999)
            username = user_data.email.split("@")[0] + str(random_suffix)

        new_user = await UserRepository.create_user(
            db=db,
            email=user_data.email,
            username=username,
            password_hash=hashed_pw,
            is_verified=False,
        )

        token = await VerificationMailTokenRepository.create_mail_verif_token(
            db=db, user_id=new_user.idUser
        )

        activation_link = (
            f"{RegisterController.web_url}/verify-email?token={token.token}"
        )

        EmailSender.send_email(
            to_email=new_user.email,
            username=new_user.username,
            activation_link=activation_link,
        )

        return {"message": "Account successfully created"}
