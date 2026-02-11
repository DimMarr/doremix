from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    idToken = Column("idToken", Integer, primary_key=True)
    token = Column("token", String(255), unique=True, nullable=False)
    idUser = Column(
        "idUser",
        Integer,
        ForeignKey("users.idUser", ondelete="CASCADE"),
        nullable=False,
    )
    createdAt = Column(
        "createdAt", DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    expiresAt = Column("expiresAt", DateTime, nullable=False)

    user = relationship("Users", back_populates="refresh_token")

    @property
    def is_valid(self):
        return datetime.now(timezone.utc) < self.expiresAt
