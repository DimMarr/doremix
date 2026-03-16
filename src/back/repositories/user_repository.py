from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.user import User, UserRole
from models.group import GroupUser, UserGroup

_ROLE_GROUP_NAME = {
    UserRole.USER: "Utilisateurs normaux",
    UserRole.MODERATOR: "Modérateurs",
    UserRole.ADMIN: "Admins",
}


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
            isVerified=is_verified,
            banned=False,
        )

        db.add(db_user)
        db.flush()  # get db_user.idUser before commit

        # Assign default base role group
        default_group = (
            db.query(UserGroup)
            .filter(UserGroup.groupName == "Utilisateurs normaux")
            .first()
        )
        if default_group:
            db.add(
                GroupUser(
                    idUser=db_user.idUser,
                    idGroup=default_group.idGroup,
                    isBaseRole=True,
                )
            )

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
        target_group = (
            db.query(UserGroup)
            .filter(UserGroup.groupName == _ROLE_GROUP_NAME[new_role])
            .first()
        )
        if not target_group:
            return None

        base_membership = (
            db.query(GroupUser)
            .filter(GroupUser.idUser == user_id, GroupUser.isBaseRole)
            .first()
        )
        if base_membership:
            base_membership.idGroup = target_group.idGroup
        else:
            db.add(
                GroupUser(idUser=user_id, idGroup=target_group.idGroup, isBaseRole=True)
            )

        db.commit()
        return db.query(User).filter(User.idUser == user_id).first()

    @staticmethod
    def get_non_admin_ban_candidates(db: Session, current_user_id: int):
        admin_group = (
            db.query(UserGroup).filter(UserGroup.groupName == "Admins").first()
        )
        admin_user_ids_subq = (
            (
                db.query(GroupUser.idUser)
                .filter(
                    GroupUser.idGroup == admin_group.idGroup,
                    GroupUser.isBaseRole,
                )
                .subquery()
            )
            if admin_group
            else None
        )

        q = db.query(User).filter(
            User.idUser != current_user_id,
            User.banned.is_(False),
        )
        if admin_user_ids_subq is not None:
            q = q.filter(User.idUser.not_in(admin_user_ids_subq))
        return q.order_by(User.idUser.asc()).all()
