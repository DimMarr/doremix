from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from database import get_db
from models.group import UserGroup
from schemas.group import GroupResponse
from middleware.auth_middleware import get_current_user_id

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    dependencies=[Depends(get_current_user_id)],
)


@router.get("/", response_model=List[GroupResponse])
async def get_all_groups(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserGroup))
    return result.scalars().all()
