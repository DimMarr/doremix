from sqlalchemy.orm import Session
from models import User


class UserController:
    @staticmethod
    def get_all_users(db: Session):
        return db.query(User).all()

    @staticmethod
    def get_user(db: Session, idUser: int):
        return db.query(User).filter(User.idUser == idUser).first()

    @staticmethod
    def get_user_playlists(db: Session, idUser: int):
        user = db.query(User).filter(User.idUser == idUser).first()
        if user:
            return user.playlists
        return []
