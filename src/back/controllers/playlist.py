from sqlalchemy.ext.asyncio import AsyncSession
from repositories import PlaylistRepository
from fastapi import HTTPException, UploadFile
from models.enums import PlaylistVisibility
from utils.image_processor import save_cover_image
from models import Playlist
from models import User


class PlaylistController:
    @staticmethod
    async def get_accessible_playlists(db: AsyncSession, user_id: int):
        return await PlaylistRepository.get_accessible_playlists(db, user_id)

    @staticmethod
    async def get_public_playlists(db: AsyncSession, user: User):
        return await PlaylistRepository.get_public_playlists(db, user)

    @staticmethod
    async def get_shared_playlists(db: AsyncSession, user_id: int):
        return await PlaylistRepository.get_shared_playlist(db, user_id)

    @staticmethod
    async def get_playlist(db: AsyncSession, playlist_id: int, user: User):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id, user)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return playlist

    @staticmethod
    async def get_playlist_tracks(db: AsyncSession, playlist_id: int, user: User):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id, user)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return await PlaylistRepository.get_playlist_tracks(db, playlist_id)

    @staticmethod
    async def upload_cover(
        db: AsyncSession, playlist_id: int, file: UploadFile, user: User
    ):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id, user)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        cover_path = save_cover_image(file, playlist_id)
        updated_playlist = await PlaylistRepository.update_cover_image(
            db, playlist_id, cover_path
        )
        return updated_playlist

    @staticmethod
    async def remove_track(
        db: AsyncSession, playlist_id: int, track_id: int, user: User
    ):
        playlist = await PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        removed = await PlaylistRepository.remove_track(db, playlist_id, track_id)
        if not removed:
            raise HTTPException(
                status_code=404, detail="This track is not in the current playlist"
            )
        await db.refresh(playlist)
        return playlist

    @staticmethod
    async def search(db: AsyncSession, query: str, user_id: int):
        if not query or len(query) < 2:
            raise HTTPException(
                status_code=400, detail="Query must be at least 2 characters"
            )
        return await PlaylistRepository.search_playlists(db, query, user_id)

    @staticmethod
    async def create_playlist(db: AsyncSession, playlist_data: dict, user_id: int):
        new_playlist = Playlist(
            name=playlist_data["name"],
            idGenre=playlist_data["idGenre"],
            visibility=playlist_data["visibility"],
            idOwner=user_id,
        )
        return await PlaylistRepository.create(db, new_playlist)

    @staticmethod
    async def delete_playlist(db: AsyncSession, playlist_id: int, user: User):
        playlist = await PlaylistRepository.get_by_id_raw(db, playlist_id)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        if not (playlist.idOwner == user.idUser or user.idRole == 3):
            raise HTTPException(
                status_code=403, detail="You're not allowed to delete this playlist."
            )

        await PlaylistRepository.delete(db, playlist)
        return {"message": f"Playlist '{playlist.name}' successfully deleted"}

    @staticmethod
    async def update_playlist(
        db: AsyncSession, playlist_id: int, update_data: dict, user: User
    ):
        playlist = await PlaylistRepository.get_by_id(db, playlist_id, user)
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist not found")

        users, _ = await PlaylistRepository.list_shared_user(
            db, playlist_id, user.idUser
        )
        editors = [u.idUser for u in users if u.editor]

        if not (
            playlist.idOwner == user.idUser
            or user.idRole == 3
            or user.idUser in editors
        ):
            raise HTTPException(
                status_code=403, detail="You're not allowed to update this playlist."
            )

        if update_data.get("visibility") == PlaylistVisibility.OPEN:
            update_data["idOwner"] = 1

        return await PlaylistRepository.update_playlist(db, playlist, update_data)

    @staticmethod
    async def add_playlist_track_secure(
        db: AsyncSession, title: str, url: str, playlist_id: int, user_id: int
    ):
        if not await PlaylistRepository.can_edit_playlist(db, playlist_id, user_id):
            raise HTTPException(
                status_code=403,
                detail="Permission denied : You don't have permission to edit this playlist",
            )

        track, status = await PlaylistRepository.add_track(db, title, url, playlist_id)

        if status == "invalid url":
            raise HTTPException(400, "Invalid URL")
        if status == "already_exists":
            raise HTTPException(409, "Track already exists")
        if not track:
            raise HTTPException(500, "Failed to add track")

        return track

    @staticmethod
    async def shared_with(db: AsyncSession, playlist_id: int, current_user_id: int):
        users, err = await PlaylistRepository.list_shared_user(
            db, playlist_id, current_user_id
        )
        if err:
            raise HTTPException(403, err)
        return users

    @staticmethod
    async def share_user(
        db: AsyncSession, playlist_id: int, owner_id: int, email: str, is_editor: bool
    ):
        success, msg = await PlaylistRepository.share_with_user(
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
    async def share_group(
        db: AsyncSession, playlist_id: int, owner_id: int, group_name: str
    ):
        success, msg = await PlaylistRepository.share_with_group(
            db, playlist_id, owner_id, group_name
        )
        if msg == "forbidden":
            raise HTTPException(403, "Forbidden")
        if msg == "group_not_found":
            raise HTTPException(404, "Group not found")
        return {"message": "Shared with group successfully"}

    @staticmethod
    async def unshare_user(
        db: AsyncSession, playlist_id: int, target_user_id: int, current_user_id: int
    ):
        success, msg = await PlaylistRepository.remove_shared_user(
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
