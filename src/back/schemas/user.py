from pydantic import BaseModel, ConfigDict, field_validator
from enum import Enum
from typing import Optional, List
from .playlist import PlaylistSchema
import re  # for regex operations


class UserRole(str, Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class UserSchema(BaseModel):
    idUser: int
    email: str
    username: str
    role: UserRole
    banned: bool
    isVerified: bool
    playlists: Optional[List[PlaylistSchema]] = None

    model_config = ConfigDict(from_attributes=True)


class ModerationUserSchema(BaseModel):
    idUser: int
    email: str
    username: str
    role: UserRole
    banned: bool

    model_config = ConfigDict(from_attributes=True)


class BanUserResponse(BaseModel):
    idUser: int
    banned: bool
    detail: str


class UserRegisterSchema(BaseModel):
    email: str
    password: str

    @field_validator("password")
    def validate_password(cls, password):
        if not re.match(
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[#?!@$%^&*-])[A-Za-z\d#?!@$%^&*-]{8,}$",
            password,
        ):
            raise ValueError(
                "Password must be at least 8 characters and contains one uppercase, one lowercase, one digit and one special character."
            )
        return password

    @field_validator("email")
    def validate_email(cls, email):
        if not re.match(
            r"^[a-zA-Z0-9._-]+@(etu\.)?umontpellier\.fr$", email
        ):  # name.lastname@[et].umontpellier.fr
            raise ValueError("Invalid email format")
        return email
