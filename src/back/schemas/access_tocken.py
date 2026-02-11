from pydantic import BaseModel, ConfigDict


class AccessTokenSchema(BaseModel):
    idToken: int
    token: str
    idUser: int
    createdAt: str
    expiresAt: str

    model_config = ConfigDict(from_attributes=True)