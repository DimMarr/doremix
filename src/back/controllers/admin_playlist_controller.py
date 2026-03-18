from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories import PlaylistRepository
from models import User


class AdminPlaylistController:

    @staticmethod
    def get_all(db: Session):
        return PlaylistRepository.get_all(db)

    @staticmethod
    def get_tracks(db: Session, playlist_id: int):
        playlist = PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return PlaylistRepository.get_playlist_tracks(db, playlist_id)

    @staticmethod
    def update_playlist(db: Session, playlist_id: int, update_data: dict):
        playlist = PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return PlaylistRepository.update_playlist(db, playlist, update_data)

    @staticmethod
    def delete_playlist(db: Session, playlist_id: int):
        playlist = PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        PlaylistRepository.delete(db, playlist)
        return {"message": f"Playlist '{playlist.name}' successfully deleted"}

    @staticmethod
    def add_track(db: Session, playlist_id: int, title: str, url: str):
        playlist = PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        result = PlaylistRepository.add_track(db, title, url, playlist_id)
        if result is None or not isinstance(result, tuple):
            raise HTTPException(status_code=500, detail="Failed to add track")

        track, status = result
        if status == "invalid url":
            raise HTTPException(status_code=400, detail="Invalid URL")
        if status == "already_exists":
            raise HTTPException(status_code=409, detail="Track already exists in this playlist")
        return track

    @staticmethod
    def remove_track(db: Session, playlist_id: int, track_id: int):
        playlist = PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if not PlaylistRepository.remove_track(db, playlist_id, track_id):
            raise HTTPException(status_code=404, detail="This track is not in the current playlist")
        db.refresh(playlist)
        return playlist
