from sqlalchemy.orm import Session
from repositories import PlaylistRepository
from models import Playlist
from fastapi import HTTPException, UploadFile
from utils import save_cover_image


class PlaylistController:
    @staticmethod
    def get_all_playlists(db: Session):
        return PlaylistRepository.get_all(db)

    @staticmethod
    def get_playlist(db: Session, playlist_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist

    @staticmethod
    def get_playlist_tracks(db: Session, playlist_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist.tracks

    @staticmethod
    def upload_cover(db: Session, playlist_id: int, file: UploadFile):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        cover_path = save_cover_image(file, playlist_id)

        updated_playlist = PlaylistRepository.update_cover_image(
            db, playlist_id, cover_path
        )

        return updated_playlist
