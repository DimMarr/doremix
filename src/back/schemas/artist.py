from pydantic import BaseModel


class ArtistSchema(BaseModel):
    idArtist: int
    name: str

    class Config:
        from_attributes = True
