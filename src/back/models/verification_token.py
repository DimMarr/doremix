from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class VerificationToken(Base):
    __tablename__ = "verification_token"

    idToken = Column("idtoken", Integer, primary_key=True)
    token = Column("token", String(255), unique=True, nullable=False)
    idUser = Column(
        "idUser",
        Integer,
        ForeignKey("users.iduser", ondelete="CASCADE"),
        nullable=False,
    )
    createdAt = Column(
        "createdat",
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expiresAt = Column("expiresat", DateTime(timezone=True), nullable=False)

    user = relationship("Users", back_populates="verification_token")

    @property
    def is_valid(self):
        return datetime.now(timezone.utc) < self.expiresAt
