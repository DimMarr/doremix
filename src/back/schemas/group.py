from pydantic import BaseModel


class GroupResponse(BaseModel):
    idGroup: int
    groupName: str

    class Config:
        from_attributes = True


class GroupCreate(BaseModel):
    groupName: str


class GroupMemberResponse(BaseModel):
    idUser: int
    username: str
    email: str


class GroupWithUsersResponse(BaseModel):
    idGroup: int
    groupName: str
    users: list[GroupMemberResponse]
