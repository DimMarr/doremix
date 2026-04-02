import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from models import Track, Playlist
from models.enums import PlaylistVisibility
from models.track_like import TrackLike


@pytest_asyncio.fixture
async def sample_track(db: AsyncSession):
    """Crée un track de test."""
    track = Track(
        title="Bohemian Rhapsody",
        youtubeLink="https://www.youtube.com/watch?v=fJ9rUzIMt7o",
    )
    db.add(track)
    await db.commit()
    await db.refresh(track)
    return track


@pytest_asyncio.fixture
async def second_track(db: AsyncSession):
    """Crée un second track de test."""
    track = Track(
        title="Stairway to Heaven",
        youtubeLink="https://www.youtube.com/watch?v=QkF3oxziUI4",
    )
    db.add(track)
    await db.commit()
    await db.refresh(track)
    return track


@pytest_asyncio.fixture
async def liked_playlist(db: AsyncSession, sample_user):
    """Crée une playlist 'Liked Tracks' existante pour l'utilisateur."""
    playlist = Playlist(
        name="Liked Tracks",
        idOwner=sample_user.idUser,
        isLikedPlaylist=True,
        idGenre=1,
    )
    db.add(playlist)
    await db.commit()
    await db.refresh(playlist)
    return playlist


# ─── GET /tracks/{id}/like ────────────────────────────────────────────────────


class TestGetLikeStatus:
    @pytest.mark.asyncio
    async def test_status_not_liked(self, client, sample_track):
        """Retourne isLiked=False pour un track non liké."""
        response = await client.get(f"/tracks/{sample_track.idTrack}/like")
        assert response.status_code == 200
        data = response.json()
        assert data["isLiked"] is False
        assert data["trackId"] == sample_track.idTrack

    @pytest.mark.asyncio
    async def test_status_liked(
        self, client, db: AsyncSession, sample_user, sample_track
    ):
        """Retourne isLiked=True après avoir liké le track."""
        like = TrackLike(idUser=sample_user.idUser, idTrack=sample_track.idTrack)
        db.add(like)
        await db.commit()

        response = await client.get(f"/tracks/{sample_track.idTrack}/like")
        assert response.status_code == 200
        data = response.json()
        assert data["isLiked"] is True

    @pytest.mark.asyncio
    async def test_status_nonexistent_track(self, client):
        """Retourne isLiked=False même pour un track inexistant (pas de 404)."""
        response = await client.get("/tracks/9999/like")
        assert response.status_code == 200
        data = response.json()
        assert data["isLiked"] is False


# ─── POST /tracks/{id}/like ───────────────────────────────────────────────────


class TestLikeTrack:
    @pytest.mark.asyncio
    async def test_like_success(self, client, sample_track):
        """Like un track avec succès."""
        response = await client.post(f"/tracks/{sample_track.idTrack}/like")
        assert response.status_code == 200
        data = response.json()
        assert data["isLiked"] is True
        assert data["trackId"] == sample_track.idTrack

    @pytest.mark.asyncio
    async def test_like_creates_liked_playlist(
        self, client, db: AsyncSession, sample_user, sample_track
    ):
        """Liker un track crée automatiquement la playlist 'Liked Tracks'."""
        await client.post(f"/tracks/{sample_track.idTrack}/like")

        from sqlalchemy.future import select

        result = await db.execute(
            select(Playlist).filter(
                Playlist.idOwner == sample_user.idUser,
                Playlist.isLikedPlaylist.is_(True),
            )
        )
        playlist = result.scalars().first()
        assert playlist is not None
        assert playlist.isLikedPlaylist is True

    @pytest.mark.asyncio
    async def test_like_reuses_existing_liked_playlist(
        self,
        client,
        db: AsyncSession,
        sample_user,
        sample_track,
        second_track,
        liked_playlist,
    ):
        """Liker plusieurs tracks réutilise la même playlist 'Liked Tracks'."""
        await client.post(f"/tracks/{sample_track.idTrack}/like")
        await client.post(f"/tracks/{second_track.idTrack}/like")

        from sqlalchemy.future import select

        result = await db.execute(
            select(Playlist).filter(
                Playlist.idOwner == sample_user.idUser,
                Playlist.isLikedPlaylist.is_(True),
            )
        )
        playlists = result.scalars().all()
        assert len(playlists) == 1

    @pytest.mark.asyncio
    async def test_like_not_found(self, client):
        """Retourne 404 si le track n'existe pas."""
        response = await client.post("/tracks/9999/like")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_like_already_liked(self, client, sample_track):
        """Retourne 409 si le track est déjà liké."""
        await client.post(f"/tracks/{sample_track.idTrack}/like")
        response = await client.post(f"/tracks/{sample_track.idTrack}/like")
        assert response.status_code == 409


# ─── DELETE /tracks/{id}/like ─────────────────────────────────────────────────


class TestUnlikeTrack:
    @pytest.mark.asyncio
    async def test_unlike_success(self, client, sample_track, second_track):
        """Unlike un track avec succès (playlist non vide donc non supprimée)."""
        await client.post(f"/tracks/{sample_track.idTrack}/like")
        await client.post(f"/tracks/{second_track.idTrack}/like")
        response = await client.delete(f"/tracks/{sample_track.idTrack}/like")
        assert response.status_code == 200
        data = response.json()
        assert data["isLiked"] is False
        assert data["trackId"] == sample_track.idTrack

    @pytest.mark.asyncio
    async def test_unlike_not_liked(self, client, sample_track):
        """Retourne 404 si le track n'est pas liké."""
        response = await client.delete(f"/tracks/{sample_track.idTrack}/like")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unlike_not_found(self, client):
        """Retourne 404 si le track n'existe pas."""
        response = await client.delete("/tracks/9999/like")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_unlike_updates_like_status(self, client, sample_track, second_track):
        """Après unlike, isLiked repasse à False."""
        await client.post(f"/tracks/{sample_track.idTrack}/like")
        await client.post(f"/tracks/{second_track.idTrack}/like")
        await client.delete(f"/tracks/{sample_track.idTrack}/like")

        response = await client.get(f"/tracks/{sample_track.idTrack}/like")
        assert response.json()["isLiked"] is False

    @pytest.mark.asyncio
    async def test_unlike_last_track_deletes_playlist(
        self, client, db: AsyncSession, sample_user, sample_track, liked_playlist
    ):
        """Unlike du dernier track supprime automatiquement la playlist 'Liked Tracks'."""
        await client.post(f"/tracks/{sample_track.idTrack}/like")
        await client.delete(f"/tracks/{sample_track.idTrack}/like")

        from sqlalchemy.future import select

        result = await db.execute(
            select(Playlist).filter(
                Playlist.idOwner == sample_user.idUser,
                Playlist.isLikedPlaylist.is_(True),
            )
        )
        playlist = result.scalars().first()
        assert playlist is None

    @pytest.mark.asyncio
    async def test_unlike_non_last_track_keeps_playlist(
        self,
        client,
        db: AsyncSession,
        sample_user,
        sample_track,
        second_track,
        liked_playlist,
    ):
        """Unlike d'un track non-dernier ne supprime pas la playlist."""
        await client.post(f"/tracks/{sample_track.idTrack}/like")
        await client.post(f"/tracks/{second_track.idTrack}/like")
        await client.delete(f"/tracks/{sample_track.idTrack}/like")

        from sqlalchemy.future import select

        result = await db.execute(
            select(Playlist).filter(
                Playlist.idOwner == sample_user.idUser,
                Playlist.isLikedPlaylist.is_(True),
            )
        )
        playlist = result.scalars().first()
        assert playlist is not None


# ─── Guards playlist likée ─────────────────────────────────────────────────────


class TestLikedPlaylistGuards:
    @pytest.mark.asyncio
    async def test_cannot_delete_liked_playlist(self, client, liked_playlist):
        """Impossible de supprimer la playlist 'Liked Tracks'."""
        response = await client.delete(f"/playlists/{liked_playlist.idPlaylist}")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_cannot_update_liked_playlist(self, client, liked_playlist):
        """Impossible de modifier la playlist 'Liked Tracks'."""
        response = await client.patch(
            f"/playlists/{liked_playlist.idPlaylist}",
            json={"name": "Nouveau nom"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_can_delete_normal_playlist(self, client, sample_playlist):
        """Une playlist normale peut être supprimée."""
        response = await client.delete(f"/playlists/{sample_playlist.idPlaylist}")
        assert response.status_code == 200


# ─── isLiked dans les tracks d'une playlist ───────────────────────────────────


class TestPlaylistTracksIsLiked:
    @pytest.mark.asyncio
    async def test_tracks_have_is_liked_false_by_default(
        self, client, sample_playlist, sample_track
    ):
        """Les tracks d'une playlist ont isLiked=False par défaut."""
        await client.post(
            f"/playlists/{sample_playlist.idPlaylist}/tracks/by-url",
            json={"title": sample_track.title, "url": sample_track.youtubeLink},
        )
        response = await client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        assert response.status_code == 200
        tracks = response.json()
        assert len(tracks) >= 1
        for track in tracks:
            assert track["isLiked"] is False

    @pytest.mark.asyncio
    async def test_tracks_have_is_liked_true_after_like(
        self, client, sample_playlist, sample_track
    ):
        """Les tracks d'une playlist ont isLiked=True après un like."""
        await client.post(
            f"/playlists/{sample_playlist.idPlaylist}/tracks/by-url",
            json={"title": sample_track.title, "url": sample_track.youtubeLink},
        )
        await client.post(f"/tracks/{sample_track.idTrack}/like")

        response = await client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        assert response.status_code == 200
        tracks = response.json()
        liked_track = next(
            (t for t in tracks if t["idTrack"] == sample_track.idTrack), None
        )
        assert liked_track is not None
        assert liked_track["isLiked"] is True

    @pytest.mark.asyncio
    async def test_tracks_is_liked_resets_after_unlike(
        self, client, sample_playlist, sample_track, second_track
    ):
        """isLiked repasse à False après un unlike (second_track garde la playlist active)."""
        await client.post(
            f"/playlists/{sample_playlist.idPlaylist}/tracks/by-url",
            json={"title": sample_track.title, "url": sample_track.youtubeLink},
        )
        await client.post(f"/tracks/{sample_track.idTrack}/like")
        await client.post(f"/tracks/{second_track.idTrack}/like")
        await client.delete(f"/tracks/{sample_track.idTrack}/like")

        response = await client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        tracks = response.json()
        liked_track = next(
            (t for t in tracks if t["idTrack"] == sample_track.idTrack), None
        )
        assert liked_track is not None
        assert liked_track["isLiked"] is False
