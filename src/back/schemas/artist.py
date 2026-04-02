from pydantic import BaseModel, ConfigDict


class ArtistSchema(BaseModel):
    idArtist: int
    name: str
    imageUrl: str | None = None

    model_config = ConfigDict(from_attributes=True)
