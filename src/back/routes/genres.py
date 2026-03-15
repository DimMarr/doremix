from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from controllers import GenreController
from schemas import GenreSchema, GenreCreate, GenreUpdate
from database import get_db
from middleware.auth_middleware import get_current_user
from models.user import User
from models.enums import Actions, Ressources
from services.permission_service import PermissionService

router = APIRouter(prefix="/genres", tags=["Genres"])
admin_router = APIRouter(prefix="/admin/genres", tags=["Admin Genres"])


@router.get(
    "/",
    response_model=list[GenreSchema],
    summary="List all genres",
    description="Returns the complete list of available genres.",
)
async def get_all_genres(db: AsyncSession = Depends(get_db)):
    return await GenreController.get_all_genres(db)


@admin_router.post(
    "/",
    response_model=GenreSchema,
    summary="Create a new genre",
    description="Create a new genre. Reserved for administrators.",
)
async def create_genre(
    body: GenreCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return await GenreController.create_genre(db, body.label)


@admin_router.put(
    "/{genre_id}",
    response_model=GenreSchema,
    summary="Modify a genre",
    description="Update name of a genre. Reserved for administrators.",
)
async def update_genre(
    genre_id: int,
    body: GenreUpdate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    return await GenreController.update_genre(db, genre_id, body.label)


@admin_router.delete(
    "/{genre_id}",
    response_model=dict,
    summary="Delete a genre",
    description="Delete a genre if it is not used by any playlist. Reserved for administrators.",
)
async def delete_genre(
    genre_id: int,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_role(["ADMIN"])),
):
    await GenreController.delete_genre(db, genre_id)
    return {"detail": "Genre supprimé avec succès"}
