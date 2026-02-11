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


class UserRegisterSchema(BaseModel):
    email: str
    password: str

    @field_validator("email")
    def validate_email(cls, email):
        if not re.match(
            r"^[a-zA-Z0-9._-]+@(etu\.)?umontpellier\.fr$", email
        ):  # name.lastname@[et].umontpellier.fr
            raise ValueError("Invalid email format")
        return email
