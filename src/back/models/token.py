from database import Base
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum


class TokenTypes(enum.Enum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"
    VERIFICATION = "VERIFICATION"
    RESET = "RESET"


class Token(Base):
    __tablename__ = "token"

    idToken = Column("idtoken", Integer, primary_key=True)
    token = Column("token", String(255), unique=True, nullable=False)
    type = Column("type", Enum(TokenTypes), name='token_type', nullable=False)
    idUser = Column("userid", Integer, ForeignKey("users.iduser", ondelete="CASCADE"), nullable=False)
    createdAt = Column("createdat", DateTime, default=datetime.now(timezone.utc), nullable=False)
    expiresAt = Column("expiresat", DateTime, nullable=False)
    
    user = relationship("User", back_populates="tokens")

    @property
    def is_valid(self):
        return datetime.now(timezone.utc) < self.expiresAt