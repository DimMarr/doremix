from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.user import User, UserRole


class UserRepository:
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
    def get_by_email_or_username(db: Session, email: str, username: str):
        return (
            db.query(User)
            .filter(or_(User.email == email, User.username == username))
            .first()
        )

    @staticmethod
    def create_user(db: Session, email: str, username: str, password_hash: str):
        db_user = User(
            email=email,
            username=username,
            password=password_hash,
            role=UserRole.USER,  # default role
            banned=False,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

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
