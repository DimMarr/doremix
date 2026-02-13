from pydantic import BaseModel, EmailStr, Field


class LoginSchema(BaseModel):
    """
    Schéma pour la requête de login
    """

    email: EmailStr = Field(..., description="Email de l'utilisateur")
    password: str = Field(
        ..., min_length=6, description="Mot de passe de l'utilisateur"
    )


class TokenResponse(BaseModel):
    """
    Schéma pour la réponse après login/refresh
    """

    access_token: str
    refresh_token: str | None = None
    user: dict


class RefreshTokenSchema(BaseModel):
    """
    Schéma pour la requête de refresh token
    (si vous voulez passer le token dans le body au lieu des cookies)
    """

    refresh_token: str = Field(
        ..., description="Refresh token pour obtenir un nouveau access token"
    )


class LogoutResponse(BaseModel):
    """
    Schéma pour la réponse de logout
    """

    message: str


class UserInfoResponse(BaseModel):
    """
    Schéma pour les informations de l'utilisateur
    """

    id: int
    email: str
    username: str
    role: str
    banned: bool
    isVerified: bool
