from pydantic import BaseModel


class GroupResponse(BaseModel):
    idGroup: int
    groupName: str

    class Config:
        from_attributes = True
