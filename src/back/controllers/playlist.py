from sqlalchemy.orm import Session
from models import Playlist

class PlaylistController:

    @staticmethod
    def get_all_playlists(db: Session):
        return db.query(Playlist).all()

    def get_playlist(db: Session, idPlaylist: int):
        return db.query(Playlist).filter(Playlist.idPlaylist == idPlaylist).first()

    def get_playlist_tracks(db: Session, idPlaylist: int):
        playlist = db.query(Playlist).filter(Playlist.idPlaylist == idPlaylist).first()
        if playlist:
            return playlist.tracks
        return []