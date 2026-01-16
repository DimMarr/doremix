from pydantic import BaseModel, ConfigDict


class ArtistSchema(BaseModel):
    idArtist: int
    name: str

    model_config = ConfigDict(from_attributes=True)
