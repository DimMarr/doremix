from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse 
from sqlalchemy.orm import Session
from typing import List

from controllers import PlaylistController
from schemas import PlaylistSchema, TrackSchema, PlaylistCreate, PlaylistUpdate
from database import get_db
import os

router = APIRouter(prefix='/playlists', tags=['Playlists'])

@router.post(
    "/",
    response_model=PlaylistSchema,
    summary="Créer une playlist",
    description="Crée une nouvelle playlist avec les informations fournies.",
)
def create_playlist(playlist: PlaylistCreate, db: Session = Depends(get_db)):
    # TODO: Quand l'auth sera en place :
    # def create_playlist(playlist: PlaylistCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    #     return PlaylistController.create_playlist(db, playlist.model_dump(), current_user)
    return PlaylistController.create_playlist(db, playlist.model_dump())

@router.get(
    "/",
    response_model=List[PlaylistSchema],
    summary="Lister toutes les playlists",
    description="Retourne la liste complète des playlists disponibles."
)
def get_playlists(db: Session = Depends(get_db)):
    playlists = PlaylistController.get_all_playlists(db)
    return playlists

@router.get(
    '/{idPlaylist}',
    response_model=PlaylistSchema,
    summary="Récupérer une playlist",
    description="Retourne les informations détaillées d'une playlist à partir de son identifiant."
)
def get_playlist(idPlaylist: int, db: Session = Depends(get_db)):
    playlist = PlaylistController.get_playlist(db, idPlaylist)
    return playlist

@router.get('/{playlist_id}/tracks', response_model=List[TrackSchema])
def get_playlist_tracks(playlist_id: int, db: Session = Depends(get_db)):
    tracks = PlaylistController.get_playlist_tracks(db, playlist_id)
    return tracks

@router.post('/{playlist_id}/cover', response_model=PlaylistSchema)
def upload_playlist_cover(
    playlist_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    updated_playlist = PlaylistController.upload_cover(db, playlist_id, file)
    return updated_playlist

@router.get('/covers/{filename}')
def get_cover_image(filename: str):
    filepath = f"/app/uploads/covers/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(filepath)

@router.delete(
    "/{identifier}",
    response_model=dict,
    summary="Delete a playlist",
    description="Deletes a playlist by its ID or name.",
)
def delete_playlist(identifier: str, db: Session = Depends(get_db)):
    # TODO: Quand l'auth sera en place :
    # def delete_playlist(identifier: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    #     return PlaylistController.delete_playlist(db, identifier, current_user.id)

    return PlaylistController.delete_playlist(db, identifier)

@router.get(
    "/name/{name}",
    response_model=List[PlaylistSchema],
    summary="Get playlists by name",
    description="Returns all playlists matching the given name.",
)
def get_playlist_by_name(name: str, db: Session = Depends(get_db)):
    playlists = PlaylistController.get_playlist_by_name(db, name)
    return playlists

@router.patch(
    "/{identifier}",
    response_model=PlaylistSchema,
    summary="Update a playlist",
    description="Updates a playlist by its ID or name.",
)
def update_playlist(identifier: str, playlist_data: PlaylistUpdate, db: Session = Depends(get_db)):
    # TODO: Quand l'auth sera en place :
    # def update_playlist(identifier: str, playlist_data: PlaylistUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    #     return PlaylistController.update_playlist(db, identifier, playlist_data.model_dump(exclude_unset=True), current_user.id)

    return PlaylistController.update_playlist(db, identifier, playlist_data.model_dump(exclude_unset=True))