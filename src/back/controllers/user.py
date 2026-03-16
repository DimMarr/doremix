from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from repositories.user_repository import UserRepository
from repositories.access_token_repository import AccessTokenRepository
from repositories.refresh_token_repository import RefreshTokenRepository


class UserController:
    @staticmethod
    def get_all_users(db: Session):
        return UserRepository.get_all(db)

    @staticmethod
    def get_all_verified_users(db: Session):
        return db.query(User).filter(User.isVerified).all()

    @staticmethod
    def get_user(db: Session, idUser: int):
        user = UserRepository.get_user_by_id(db, idUser)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {idUser} not found",
            )
        return user

    @staticmethod
    def get_user_playlists(db: Session, idUser: int):
        user = UserRepository.get_user_by_id(db, idUser)
        if user:
            return user.playlists
        return []

    @staticmethod
    def get_ban_candidates(db: Session, moderator_id: int):
        return UserRepository.get_non_admin_ban_candidates(db, moderator_id)

    @staticmethod
    def ban_user(db: Session, moderator_id: int, target_user_id: int):
        if moderator_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot ban yourself",
            )

        target_user = UserRepository.get_user_by_id(db, target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {target_user_id} not found",
            )

        # if target_user.idRole == UserRepository.ADMIN_ROLE_ID:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Moderators cannot ban admin users",
        #     )

        try:
            target_user.banned = True
            AccessTokenRepository.revoke_all_user_tokens(
                db, target_user_id, commit=False
            )
            RefreshTokenRepository.revoke_all_user_tokens(
                db, target_user_id, commit=False
            )
            db.commit()
            db.refresh(target_user)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to ban user: {str(e)}",
            )

        return target_user
