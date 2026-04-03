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


class UserBanStatusResponse(BaseModel):
    idUser: int
    banned: bool
    detail: str


class UserRegisterSchema(BaseModel):
    email: str
    password: str

    @field_validator("password")
    def validate_password(cls, password):
        if not re.match(
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[#?!@$%^&*_-])[A-Za-z\d#?!@$%^&*_-]{8,}$",
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


class SharedUserSchema(BaseModel):
    idUser: int
    idPlaylist: int
    editor: bool
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_user_playlist(cls, up):
        return cls(
            idUser=up.idUser,
            idPlaylist=up.idPlaylist,
            editor=up.editor,
            username=up.user.username,
            email=up.user.email,
        )
