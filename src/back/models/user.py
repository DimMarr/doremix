from sqlalchemy import Column, Integer, String, Boolean, Enum
from database import Base
import enum

class UserRole(enum.Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"
    
    idUser = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    banned = Column(Boolean, default=False)