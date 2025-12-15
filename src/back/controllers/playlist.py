from sqlalchemy.orm import Session
from models import Playlist

class PlaylistController:

    @staticmethod
    def get_all_playlists(db: Session):
        return db.query(Playlist).all()

    def get_playlist(db: Session, playlist_id: int):
        return db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()

    def get_playlist_tracks(db: Session, playlist_id: int):
        playlist = db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
        if playlist:
            return playlist.tracks
        return []