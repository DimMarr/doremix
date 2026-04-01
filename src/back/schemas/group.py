from pydantic import BaseModel, ConfigDict


class GroupSchema(BaseModel):
    idGroup: int
    groupName: str

    model_config = ConfigDict(from_attributes=True)
