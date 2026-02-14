from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class AccessToken(Base):
    __tablename__ = "access_token"

    idToken = Column("idtoken", Integer, primary_key=True)
    token = Column("token", String(255), unique=True, nullable=False)
    idUser = Column(
        "iduser",
        Integer,
        ForeignKey("users.iduser", ondelete="CASCADE"),
        nullable=False,
    )
    createdAt = Column(
        "createdat", DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    expiresAt = Column("expiresat", DateTime, nullable=False)

    @property
    def is_valid(self):
        return datetime.now(timezone.utc) < self.expiresAt
