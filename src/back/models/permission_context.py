from typing import Optional, List
from pydantic import BaseModel
from models.user import User, UserRole
from models.enums import Actions, Ressources
from models.group import UserGroup


class PermissionContext(BaseModel):
    """Encapsulates permission check context for a user action."""

    user: User
    action: Actions
    resource: Ressources
    resource_id: Optional[int] = None
    base_role: Optional[UserRole] = None
    all_groups: List[UserGroup] = []

    class Config:
        arbitrary_types_allowed = True
