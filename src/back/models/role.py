from sqlalchemy import Column, Integer, String
from database import Base


class Role(Base):
    __tablename__ = "role"

    idRole = Column("idrole", Integer, primary_key=True, index=True)
    roleName = Column(
        "rolename",
        String(255),
        unique=True,
        nullable=False,
    )
