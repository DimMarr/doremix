from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from models import User, UserRole
from repositories import UserRepository, AccessTokenRepository, RefreshTokenRepository


class UserController:
    @staticmethod
    async def get_all_users(db: AsyncSession):
        users = await UserRepository.get_all(db)
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        return users

    @staticmethod
    async def get_all_verified_users(db: AsyncSession):
        users = await UserRepository.get_all(db)
        if not users:
            raise HTTPException(status_code=404, detail="No verified users found")
        return [u for u in users if u.isVerified]

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int):
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    async def get_user_playlists(db: AsyncSession, user_id: int):
        user = await UserRepository.get_user_by_id(db, user_id)
        if user:
            return user.playlists
        return []

    @staticmethod
    async def get_ban_candidates(db: AsyncSession, moderator_id: int):
        return await UserRepository.get_non_admin_ban_candidates(db, moderator_id)

    @staticmethod
    async def ban_user(db: AsyncSession, moderator_id: int, target_user_id: int):
        if moderator_id == target_user_id:
            raise HTTPException(status_code=400, detail="You cannot ban yourself")

        target_user = await UserRepository.get_user_by_id(db, target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=404, detail=f"User {target_user_id} not found"
            )
        if target_user.idRole == UserRepository.ADMIN_ROLE_ID:
            raise HTTPException(status_code=403, detail="You cannot ban an admin user")

        try:
            target_user.banned = True
            await AccessTokenRepository.revoke_all_user_tokens(
                db, target_user_id, commit=False
            )
            await RefreshTokenRepository.revoke_all_user_tokens(
                db, target_user_id, commit=False
            )
            await db.commit()
            await db.refresh(target_user)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ban user: {str(e)}",
            )
        return target_user

    @staticmethod
    async def add_moderator(db: AsyncSession, user_id: int):
        # Check that user exists
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check that user is neither Moderator nor Admin
        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_418_IM_A_TEAPOT,
                detail="User is an admin",
            )

        if user.role != UserRole.USER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is already moderator",
            )

        updated_user = await UserRepository.update_role(db, user_id, UserRole.MODERATOR)
        return updated_user

    @staticmethod
    async def demote_moderator(db: AsyncSession, user_id: int):
        # Check that user exists
        user = await UserRepository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.role == UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_418_IM_A_TEAPOT,
                detail="User is an admin",
            )

        # Check that user is moderator
        if user.role != UserRole.MODERATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a moderator",
            )

        updated_user = await UserRepository.update_role(db, user_id, UserRole.USER)
        return updated_user
