from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.user import User, UserRole


class UserRepository:
    ADMIN_ROLE_ID = 3  # harcodé pour que les moderators ne puisse pas ban les admin

    @staticmethod
    def create(db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_all(db: Session):
        users = db.query(User).all()
        return users

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.idUser == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_username(db: Session, username: str):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(
        db: Session, email: str, username: str, password_hash: str, is_verified: bool
    ):
        db_user = User(
            email=email,
            username=username,
            password=password_hash,
            isVerified=is_verified,  # for email verification
            role=UserRole.USER,  # default role
            banned=False,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def mark_as_verified(db: Session, userId: int):
        user = db.query(User).filter(User.idUser == userId).first()
        if user:
            user.is_verified = True
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def search_users(db: Session, query: str, limit: int = 10):
        users = (
            db.query(User)
            .filter(
                or_(
                    User.username.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                )
            )
            .limit(limit)
            .all()
        )
        return users

    @staticmethod
    def update_role(db: Session, user_id: int, new_role: UserRole):
        user = db.query(User).filter(User.idUser == user_id).first()
        if user:
            user.role = new_role
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def get_non_admin_ban_candidates(db: Session, current_user_id: int):
        return (
            db.query(User)
            .filter(
                User.idUser != current_user_id,
                User.idRole != UserRepository.ADMIN_ROLE_ID,
                User.banned.is_(False),
            )
            .order_by(User.idUser.asc())
            .all()
        )
