from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import and_, or_, select
from sqlalchemy.engine import Result
from re import findall as regex_match
from typing import Optional, List, cast

from models import Playlist, PlaylistVisibility, Track, TrackPlaylist, Artist
from .track import TrackRepository
from .artist import ArtistRepository
from utils.youtube_utils import get_youtube_video_info
from schemas.playlist import PlaylistUpdate


class PlaylistRepository:
    # =========================
    # GET methods
    # =========================
    @staticmethod
    async def get_all(db: AsyncSession) -> List[Playlist]:
        result: Result[tuple[Playlist]] = await db.execute(select(Playlist))
        return cast(List[Playlist], result.scalars().all())

    @staticmethod
    async def get_public_playlists(db: AsyncSession) -> List[Playlist]:
        result: Result[tuple[Playlist]] = await db.execute(
            select(Playlist).where(Playlist.visibility == PlaylistVisibility.PUBLIC)
        )
        return cast(List[Playlist], result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, playlist_id: int) -> Optional[Playlist]:
        result: Result[tuple[Playlist]] = await db.execute(
            select(Playlist)
            .options(selectinload(Playlist.tracks).selectinload(Track.artists))
            .where(Playlist.idPlaylist == playlist_id)
        )
        return cast(Optional[Playlist], result.scalars().first())

    @staticmethod
    async def search_playlists(
        db: AsyncSession, query: str, limit: int = 10
    ) -> List[Playlist]:
        result: Result[tuple[Playlist]] = await db.execute(
            select(Playlist)
            .where(
                and_(
                    Playlist.name.ilike(f"%{query}%"),
                    Playlist.visibility == PlaylistVisibility.PUBLIC,
                )
            )
            .limit(limit)
        )
        return cast(List[Playlist], result.scalars().all())

    # =========================
    # CREATE methods
    # =========================
    @staticmethod
    async def create(db: AsyncSession, playlist: Playlist) -> Playlist:
        db.add(playlist)
        await db.commit()
        await db.refresh(playlist)
        return playlist

    @staticmethod
    async def add_track(
        db: AsyncSession, track: Track, playlist_id: int
    ) -> tuple[Optional[Track], str]:
        # Vérifier et nettoyer l'URL YouTube
        match = regex_match(
            r"(https://www\.youtube\.com/watch\?v=[^&|\s]+|https://youtu\.be/[^?|\s]+)",
            track.youtubeLink,
        )
        if not match:
            return track, "invalid url"
        clean_url = match[0]

        # Vérifier si le track existe déjà
        existing_track = await TrackRepository.get_by_youtube_link(db, clean_url)

        if not existing_track:
            # Récupérer les infos de la vidéo YouTube
            duration_seconds, author_name = get_youtube_video_info(clean_url)
            if duration_seconds is None:
                return track, "invalid url"
            if not author_name:
                author_name = "Unknown Artist"

            # Créer l'artiste si nécessaire
            artist = await ArtistRepository.create(db, author_name)

            # Créer le track avec l'artiste lié
            existing_track = await TrackRepository.create(
                db,
                Track(
                    title=track.title,
                    youtubeLink=clean_url,
                    durationSeconds=duration_seconds,
                    artists=[artist],
                ),
            )
            if not existing_track:
                return None, "failed"

        # Vérifier si le track est déjà dans la playlist
        result: Result[tuple[TrackPlaylist]] = await db.execute(
            select(TrackPlaylist).where(
                TrackPlaylist.idPlaylist == playlist_id,
                TrackPlaylist.idTrack == existing_track.idTrack,
            )
        )
        track_in_playlist = result.scalars().first()
        if track_in_playlist:
            return existing_track, "already_exists"

        # Ajouter le track à la playlist
        track_playlist = TrackPlaylist(
            idPlaylist=playlist_id, idTrack=existing_track.idTrack
        )
        db.add(track_playlist)
        await db.commit()
        await db.refresh(track_playlist)

        # Précharger les artistes pour éviter le lazy-loading
        result_artist: Result[tuple[Track]] = await db.execute(
            select(Track)
            .options(selectinload(Track.artists))
            .where(Track.idTrack == existing_track.idTrack)
        )
        existing_track = cast(Track, result_artist.scalar_one())

        return existing_track, "added"

    # =========================
    # DELETE methods
    # =========================
    @staticmethod
    async def delete(db: AsyncSession, playlist: Playlist) -> Playlist:
        await db.delete(playlist)
        await db.commit()
        return playlist

    @staticmethod
    async def remove_track(db: AsyncSession, playlist_id: int, track_id: int) -> bool:
        result: Result[tuple[TrackPlaylist]] = await db.execute(
            select(TrackPlaylist)
            .where(TrackPlaylist.idPlaylist == playlist_id)
            .where(TrackPlaylist.idTrack == track_id)
        )
        track_playlist = result.scalars().first()

        if track_playlist:
            await db.delete(track_playlist)
            await db.commit()
            return True

        return False

    # =========================
    # UPDATE methods
    # =========================
    @staticmethod
    async def update(
        db: AsyncSession, playlist: Playlist, update_data: PlaylistUpdate
    ) -> Playlist:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(playlist, key, value)

        await db.commit()
        await db.refresh(playlist)
        return playlist

    @staticmethod
    async def update_cover_image(
        db: AsyncSession, playlist_id: int, cover_path: str
    ) -> Optional[Playlist]:
        result: Result[tuple[Playlist]] = await db.execute(
            select(Playlist).where(Playlist.idPlaylist == playlist_id)
        )
        playlist = cast(Optional[Playlist], result.scalars().first())
        if playlist:
            playlist.coverImage = cover_path
            await db.commit()
            await db.refresh(playlist)
        return playlist
