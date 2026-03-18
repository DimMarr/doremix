from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from controllers import ArtistController
from schemas import ArtistSchema
from database import get_db

router = APIRouter(prefix="/artists", tags=["Artists"])


# =========================
# GET routes
# =========================


@router.get(
    "/",
    response_model=list[ArtistSchema],
    summary="Get all artists",
    description="Returns the complete list of available artists.",
)
async def get_artists(db: AsyncSession = Depends(get_db)):
    return await ArtistController.get_all_artists(db)


@router.get(
    "/{artist_id}",
    response_model=ArtistSchema,
    summary="Get an artist",
    description="Returns the detailed information of an artist based on their ID.",
)
async def get_artist(artist_id: int, db: AsyncSession = Depends(get_db)):
    return await ArtistController.get_artist(db, artist_id)
