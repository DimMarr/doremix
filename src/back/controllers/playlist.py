from sqlalchemy.orm import Session
from repositories import PlaylistRepository
from fastapi import HTTPException, UploadFile, Response
from utils.image_processor import save_cover_image
from models.playlist import Playlist


class PlaylistController:
    @staticmethod
    def get_all_playlists(db: Session):
        return PlaylistRepository.get_all(db)

    @staticmethod
    def get_public_playlists(db: Session):
        return PlaylistRepository.get_public_playlists(db)

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
    def add_playlist_track(
        db: Session,
        title: str,
        youtubeLink: str,
        playlist_id: int,
    ):
        playlist = PlaylistRepository.get_by_id(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # TODO: Quand l'auth sera en place, vérifier les permissions :
        # is_owner = playlist.idOwner == user_id
        # is_editor = PlaylistRepository.is_user_editor(db, playlist.idPlaylist, user_id)
        # is_open = playlist.visibility.value == "OPEN"
        #
        # if not (is_owner or is_editor or is_open):
        #     raise HTTPException(status_code=403, detail="You don't have permission to edit this playlist")

        track, status = PlaylistRepository.add_track(
            db, title, youtubeLink, playlist_id
        )

        if status == "invalid url":
            raise HTTPException(status_code=403, detail="Invalid YouTube URL provided")

        if track is None:
            raise HTTPException(status_code=400, detail="Failed to add track")

        if status == "already_exists":
            raise HTTPException(
                status_code=409, detail="Track already exists in this playlist"
            )
        return track

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

    @staticmethod
    def create_playlist(db: Session, playlist_data: dict):
        new_playlist = Playlist(
            name=playlist_data["name"],
            idGenre=playlist_data["idGenre"],
            visibility=playlist_data["visibility"],
            idOwner=1,  # TODO: Remplacer par current_user.id quand l'auth sera en place
        )

        return PlaylistRepository.create(db, new_playlist)

    @staticmethod
    def delete_playlist(db: Session, playlist_id: int):
        # TODO: Quand l'auth sera en place, ajouter user_id en paramètre :
        # def delete_playlist(db: Session, playlist_id: int, user_id: int):

        playlist = PlaylistRepository.get_by_id(db, playlist_id)

        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # TODO: Quand l'auth sera en place, vérifier que l'utilisateur est le propriétaire :
        # if playlist.idOwner != user_id:
        #     raise HTTPException(status_code=403, detail="You are not the owner of this playlist")

        PlaylistRepository.delete(db, playlist)

        return {"message": f"Playlist '{playlist.name}' successfully deleted"}

    @staticmethod
    def update_playlist(db: Session, playlist_id: int, update_data: dict):
        # TODO: Quand l'auth sera en place, ajouter user_id en paramètre :
        # def update_playlist(db: Session, playlist_id: int, update_data: dict, user_id: int):

        playlist = PlaylistRepository.get_by_id(db, playlist_id)

        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # TODO: Quand l'auth sera en place, vérifier que l'utilisateur est le propriétaire :
        # if playlist.idOwner != user_id:
        #     raise HTTPException(status_code=403, detail="You are not the owner of this playlist")

        return PlaylistRepository.update_playlist(db, playlist, update_data)
