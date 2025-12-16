from sqlalchemy.orm import Session
from models.playlist import Playlist
from typing import Optional, List

class PlaylistRepository:
    
    @staticmethod
    def get_all(db: Session) -> List[Playlist]:
        return db.query(Playlist).all()
    
    @staticmethod
    def get_by_id(db: Session, playlist_id: int) -> Optional[Playlist]:
        return db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
    
    @staticmethod
    def create(db: Session, playlist: Playlist) -> Playlist:
        db.add(playlist)
        db.commit()
        db.refresh(playlist)
        return playlist
    
    @staticmethod
    def update(db: Session, playlist: Playlist) -> Playlist:
        db.commit()
        db.refresh(playlist)
        return playlist
    
    @staticmethod
    def delete(db: Session, playlist: Playlist) -> None:
        db.delete(playlist)
        db.commit()
    
    @staticmethod
    def update_cover_image(db: Session, playlist_id: int, cover_path: str) -> Optional[Playlist]:
        playlist = db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
        if playlist:
            playlist.coverImage = cover_path
            db.commit()
            db.refresh(playlist)
        return playlist