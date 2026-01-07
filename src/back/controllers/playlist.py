from sqlalchemy.orm import Session
from repositories import PlaylistRepository
from models import Playlist
from fastapi import HTTPException, UploadFile, Response
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

    @staticmethod
    def remove_track(db: Session, playlist_id: int, track_id: int):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if not PlaylistRepository.remove_track(db, playlist_id, track_id):
            raise HTTPException(
                status_code=404, detail="This track is not in the current playlist"
            )

        db.refresh(playlist)

        return playlist

    @staticmethod
    def search(db: Session, query: str):
        if not query or len(query) < 2:
            raise HTTPException(
                status_code=400, detail="Query must be at least 2 characters"
            )

        playlists = PlaylistRepository.search_playlists(db, query)
        return playlists
