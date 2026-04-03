from pydantic import BaseModel


class GroupSchema(BaseModel):
    idGroup: int
    groupName: str


class GroupMemberSchema(BaseModel):
    idUser: int
    username: str
    email: str


class GroupWithUsersSchema(GroupSchema):
    users: list[GroupMemberSchema] = []
