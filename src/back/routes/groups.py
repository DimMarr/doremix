from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from typing import List
from database import get_db
from models.group import GroupUser, UserGroup
from models.user import User
from schemas.group import (
    GroupCreate,
    GroupMemberResponse,
    GroupResponse,
    GroupWithUsersResponse,
)
from middleware.auth_middleware import get_current_user_id, require_role

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    dependencies=[Depends(get_current_user_id)],
)

admin_router = APIRouter(prefix="/admin/groups", tags=["Admin Groups"])


@router.get("/", response_model=List[GroupResponse])
async def get_all_groups(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserGroup))
    return result.scalars().all()


@admin_router.get(
    "/",
    response_model=List[GroupWithUsersResponse],
    summary="List all groups with members",
    description="Returns all groups and their members. Admin only.",
)
async def admin_get_all_groups(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    groups_result = await db.execute(
        select(UserGroup).order_by(UserGroup.groupName.asc())
    )
    groups = groups_result.scalars().all()

    memberships_result = await db.execute(
        select(
            GroupUser.idGroup,
            User.idUser,
            User.username,
            User.email,
        ).join(User, User.idUser == GroupUser.idUser)
    )

    users_by_group: dict[int, list[GroupMemberResponse]] = {}
    for row in memberships_result.all():
        users_by_group.setdefault(row.idGroup, []).append(
            GroupMemberResponse(
                idUser=row.idUser,
                username=row.username,
                email=row.email,
            )
        )

    return [
        GroupWithUsersResponse(
            idGroup=group.idGroup,
            groupName=group.groupName,
            users=users_by_group.get(group.idGroup, []),
        )
        for group in groups
    ]


@admin_router.post(
    "/",
    response_model=GroupResponse,
    summary="Create group",
    description="Creates a new user group. Admin only.",
)
async def admin_create_group(
    body: GroupCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    group_name = body.groupName.strip()
    if not group_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group name cannot be empty",
        )

    existing_result = await db.execute(
        select(UserGroup).filter(func.lower(UserGroup.groupName) == group_name.lower())
    )
    if existing_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Group with this name already exists",
        )

    group = UserGroup(groupName=group_name)
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group


@admin_router.delete(
    "/{group_id}",
    response_model=dict,
    summary="Delete group",
    description="Deletes a user group. Admin only.",
)
async def admin_delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    group_result = await db.execute(
        select(UserGroup).filter(UserGroup.idGroup == group_id)
    )
    group = group_result.scalars().first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )

    await db.delete(group)
    await db.commit()
    return {"detail": "Group deleted"}


@admin_router.post(
    "/{group_id}/users/{user_id}",
    response_model=dict,
    summary="Add user to group",
    description="Adds a user to a group. Admin only.",
)
async def admin_add_user_to_group(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    group_result = await db.execute(
        select(UserGroup).filter(UserGroup.idGroup == group_id)
    )
    group = group_result.scalars().first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found",
        )

    user_result = await db.execute(select(User).filter(User.idUser == user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    existing_result = await db.execute(
        select(GroupUser).filter(
            GroupUser.idGroup == group_id,
            GroupUser.idUser == user_id,
        )
    )
    if existing_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already in this group",
        )

    membership = GroupUser(idGroup=group_id, idUser=user_id)
    db.add(membership)
    await db.commit()
    return {"detail": "User added to group"}


@admin_router.delete(
    "/{group_id}/users/{user_id}",
    response_model=dict,
    summary="Remove user from group",
    description="Removes a user from a group. Admin only.",
)
async def admin_remove_user_from_group(
    group_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    membership_result = await db.execute(
        select(GroupUser).filter(
            GroupUser.idGroup == group_id,
            GroupUser.idUser == user_id,
        )
    )
    membership = membership_result.scalars().first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not in this group",
        )

    await db.delete(membership)
    await db.commit()
    return {"detail": "User removed from group"}
