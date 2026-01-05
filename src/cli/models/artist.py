from pydantic import BaseModel


class ArtistSchema(BaseModel):
    idArtist: int
    name: str
