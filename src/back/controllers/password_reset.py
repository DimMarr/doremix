from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from repositories import PasswordResetRepository
from utils.email_sender import EmailSender


class PasswordResetController:
    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str):
        raw_code = await PasswordResetRepository.request_reset(db, email)

        if not raw_code:
            print(f"Password reset requested for non-existent email: {email}")
            return {
                "message": "If an account exists with this email, you will receive a password reset code."
            }

        try:
            from repositories import UserRepository

            user = await UserRepository.get_by_email(db, email)
            if user:
                EmailSender.send_password_reset_email(
                    to_email=user.email,
                    username=user.username,
                    code=raw_code,
                )
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
            raise HTTPException(status_code=500, detail="Failed to send reset email")

        return {
            "message": "If an account exists with this email, you will receive a password reset code."
        }

    @staticmethod
    async def verify_reset_code(db: AsyncSession, email: str, code: str):
        from repositories import UserRepository

        user = await UserRepository.get_by_email(db, email)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        result = await PasswordResetRepository.verify_code(db, user.idUser, code)

        if result == "invalid":
            raise HTTPException(status_code=400, detail="Invalid password reset code")
        if result == "expired":
            raise HTTPException(
                status_code=400, detail="Password reset code has expired"
            )

        return {"message": "Code verified, you can now reset your password"}

    @staticmethod
    async def reset_password(
        db: AsyncSession, email: str, code: str, new_password: str
    ):
        result = await PasswordResetRepository.confirm_reset(
            db, email, code, new_password
        )

        if result == "invalid":
            raise HTTPException(status_code=400, detail="Invalid password reset code")
        if result == "expired":
            raise HTTPException(
                status_code=400, detail="Password reset code has expired"
            )
        if result == "error":
            raise HTTPException(status_code=500, detail="Failed to reset password")

        return {"message": "Password reset successfully", "status": "reset"}
