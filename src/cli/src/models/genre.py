from pydantic import BaseModel


class GenresSchema(BaseModel):
    idGenre: int
    label: str
