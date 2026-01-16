from pydantic import BaseModel, ConfigDict


class GenreSchema(BaseModel):
    idGenre: int
    label: str

    model_config = ConfigDict(from_attributes=True)
