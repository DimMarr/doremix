import os
import random
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from schemas import UserRegisterSchema
from repositories import UserRepository
from passlib.context import CryptContext

# TODO: Décommenter ces imports quand la vérification email sera active
# from repositories.verification_token_repository import VerificationTokenRepository
# from utils.email_verification import EmailVerification


class RegisterController:
    pwd_context = CryptContext(schemes=["bcrypt"])
    pepper = os.getenv("PEPPER_KEY")

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

        # TODO: Passer is_verified=False une fois le système d'email en place
        # Pour l'instant, on met True pour pouvoir tester le Login direct.
        await UserRepository.create_user(
            db=db,
            email=user_data.email,
            username=username,
            password_hash=hashed_pw,
            is_verified=True,
        )

        # TODO: Email verification
        # verif_token = await VerificationTokenRepository.create_token(db, new_user.idUser)
        # EmailVerification.send_activation_email(
        #     email=new_user.email,
        #     username=new_user.username,
        #     token_brut=verif_token.token
        # )

        return {"message": "Account successfully created"}
