from sqlalchemy.orm import Session
from repositories import PlaylistRepository
from fastapi import HTTPException, UploadFile, Response
from models.enums import PlaylistVisibility
from utils.image_processor import save_cover_image
from models.playlist import Playlist
from models import User


class PlaylistController:
    @staticmethod
    def get_accessible_playlists(db: Session, user_id: int):
        return PlaylistRepository.get_accessible_playlists(db, user_id)

    @staticmethod
    def get_public_playlists(db: Session, user: User):
        return PlaylistRepository.get_public_playlists(db, user)

    @staticmethod
    def get_shared_playlists(db: Session, user_id: int):
        return PlaylistRepository.get_shared_playlist(db, user_id)

    @staticmethod
    def get_playlist(db: Session, playlist_id: int, user: User):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist

    @staticmethod
    def get_playlist_tracks(db: Session, playlist_id: int, user: User):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return PlaylistRepository.get_playlist_tracks(db, playlist_id)

    @staticmethod
    def upload_cover(db: Session, playlist_id: int, file: UploadFile, user: User):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        cover_path = save_cover_image(file, playlist_id)

        updated_playlist = PlaylistRepository.update_cover_image(
            db, playlist_id, cover_path
        )

        return updated_playlist

    @staticmethod
    def remove_track(db: Session, playlist_id: int, track_id: int, user: User):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        if not PlaylistRepository.remove_track(db, playlist_id, track_id):
            raise HTTPException(
                status_code=404, detail="This track is not in the current playlist"
            )

        db.refresh(playlist)

        return playlist

    @staticmethod
    def search(db: Session, query: str, idUser: int):
        if not query or len(query) < 2:
            raise HTTPException(
                status_code=400, detail="Query must be at least 2 characters"
            )

        playlists = PlaylistRepository.search_playlists(db, query, idUser)
        return playlists

    @staticmethod
    def create_playlist(db: Session, playlist_data: dict, user_id: int):
        new_playlist = Playlist(
            name=playlist_data["name"],
            idGenre=playlist_data["idGenre"],
            visibility=playlist_data["visibility"],
            idOwner=user_id,
        )

        return PlaylistRepository.create(db, new_playlist)

    @staticmethod
    def delete_playlist(db: Session, playlist_id: int, user: User):
        playlist = PlaylistRepository.get_by_id_raw(db, playlist_id)

        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # Only playlist owner and admin can delete playlist
        if not (playlist.idOwner == user.idUser or user.idRole == 3):
            raise HTTPException(
                status_code=403, detail="You're not allowed to delete this playlist."
            )

        PlaylistRepository.delete(db, playlist)

        return {"message": f"Playlist '{playlist.name}' successfully deleted"}

    @staticmethod
    def update_playlist(db: Session, playlist_id: int, update_data: dict, user: User):
        playlist = PlaylistRepository.get_by_id(db, playlist_id, user)
        users, _ = PlaylistRepository.list_shared_user(db, playlist_id, user.idUser)
        editors = [user.idUser for user in users if user.editor]

        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        # Only playlist owner, playlist editors and admin can update playlist
        if not (
            playlist.idOwner == user.idUser
            or user.idRole == 3
            or user.idUser in editors
        ):
            raise HTTPException(
                status_code=404, detail="You're not allowed to update this playlist."
            )

        if update_data["visibility"] == PlaylistVisibility.OPEN:
            update_data["idOwner"] = 1

        return PlaylistRepository.update_playlist(db, playlist, update_data)

    @staticmethod
    def add_playlist_track_secure(
        db: Session, title: str, url: str, playlist_id: int, user_id: int
    ):
        # 1. Vérification de sécurité
        if not PlaylistRepository.can_edit_playlist(db, playlist_id, user_id):
            raise HTTPException(
                status_code=403,
                detail="Permission denied : You don't have permission to edit this playlist",
            )

        # 2. Appel de la logique métier
        track, status = PlaylistRepository.add_track(db, title, url, playlist_id)

        if status == "invalid url":
            raise HTTPException(400, "Invalid URL")
        if status == "already_exists":
            raise HTTPException(409, "Track already exists")
        if not track:
            raise HTTPException(500, "Failed to add track")

        return track

    @staticmethod
    def shared_with(db: Session, playlist_id: int, current_user_id: int):
        users, err = PlaylistRepository.list_shared_user(
            db, playlist_id, current_user_id
        )
        if err:
            raise HTTPException(403, err)
        return users

    @staticmethod
    def share_user(
        db: Session, playlist_id: int, owner_id: int, email: str, is_editor: bool
    ):
        success, msg = PlaylistRepository.share_with_user(
            db, playlist_id, owner_id, email, is_editor
        )
        if msg == "forbidden":
            raise HTTPException(403, "Forbidden")
        if msg == "user_not_found":
            raise HTTPException(404, "User not found")
        if msg == "self_share":
            raise HTTPException(400, "Cannot share with yourself")
        return {"message": "Shared successfully"}

    @staticmethod
    def share_group(db: Session, playlist_id: int, owner_id: int, group_name: str):
        success, msg = PlaylistRepository.share_with_group(
            db, playlist_id, owner_id, group_name
        )
        if msg == "forbidden":
            raise HTTPException(403, "Forbidden")
        if msg == "group_not_found":
            raise HTTPException(404, "Group not found")
        return {"message": "Shared with group successfully"}

    @staticmethod
    def unshare_user(
        db: Session, playlist_id: int, target_user_id: int, current_user_id: int
    ):
        success, msg = PlaylistRepository.remove_shared_user(
            db, playlist_id, target_user_id, current_user_id
        )
        if msg == "playlist_not_found":
            raise HTTPException(status_code=404, detail="Playlist not found")
        if msg == "forbidden":
            raise HTTPException(
                status_code=403,
                detail="You're not allowed to remove users from this playlist",
            )
        if msg == "user_not_found":
            raise HTTPException(
                status_code=404,
                detail="This user does not have access to this playlist",
            )
        return {"message": "User successfully removed from playlist"}
