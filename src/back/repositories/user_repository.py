from sqlalchemy.orm import Session
from typing import Optional
from models.user import User, UserRole


class UserRepository:
    @staticmethod
    def create_user(
        db: Session, email: str, hashed_password: str, username: str
    ) -> User:
        """Create a new user with hashed password."""
        user = User(
            email=email,
            password=hashed_password,
            username=username,
            role=UserRole.USER,
            banned=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email address."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.idUser == user_id).first()

    @staticmethod
    def update_user_role(db: Session, user_id: int, role: UserRole) -> Optional[User]:
        """Update user's role."""
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            return None
        user.role = role
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def ban_user(db: Session, user_id: int) -> Optional[User]:
        """Ban a user."""
        user = UserRepository.get_user_by_id(db, user_id)
        if not user:
            return None
        user.banned = True
        db.commit()
        db.refresh(user)
        return user
