from sqlalchemy import Column, Integer, Enum, ForeignKey
from database import Base
from .enums import Actions, Ressources


class Permissions(Base):
    __tablename__ = "permissions"

    action = Column(
        "action",
        Enum(Actions, name="actions"),
        primary_key=True,
        nullable=False,
    )
    ressource = Column(
        "ressource",
        Enum(Ressources, name="ressources"),
        primary_key=True,
        nullable=False,
    )
    groupId = Column(
        "groupid",
        Integer,
        ForeignKey("user_group.idgroup", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
