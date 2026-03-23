"""
Tests for admin playlist management endpoints: /admin/playlists/*
Follows the async pattern established in test_moderation.py.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

import pytest_asyncio
from fastapi import FastAPI, Request
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from database import get_db
from models import User, Genre
from models.enums import PlaylistVisibility
from models.playlist import Playlist
from models.track import Track
from models.track_playlist import TrackPlaylist
from routes.admin_playlists import router as admin_playlists_router


async def create_user(
    db: AsyncSession, email: str, username: str, id_role: int
) -> User:
    user = User(
        email=email,
        username=username,
        password="hashed-password",
        idRole=id_role,
        isVerified=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def make_auth_middleware(actor: User):
    class FakeAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            request.state.user = actor
            request.state.user_id = actor.idUser
            return await call_next(request)

    return FakeAuthMiddleware


def build_client(db: AsyncSession, actor: User) -> AsyncClient:
    app = FastAPI()
    app.add_middleware(make_auth_middleware(actor))
    app.include_router(admin_playlists_router)

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest_asyncio.fixture
async def sample_genre(db: AsyncSession):
    genre = Genre(label="Rock")
    db.add(genre)
    await db.commit()
    await db.refresh(genre)
    return genre


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    return await create_user(db, "admin@test.com", "admin", 3)


@pytest_asyncio.fixture
async def regular_user(db: AsyncSession):
    return await create_user(db, "regular@test.com", "regular", 1)


@pytest_asyncio.fixture
async def other_user(db: AsyncSession):
    return await create_user(db, "other@test.com", "other", 1)


@pytest_asyncio.fixture
async def sample_playlists(db: AsyncSession, other_user, sample_genre):
    playlists = [
        Playlist(
            name="Public Playlist",
            idGenre=sample_genre.idGenre,
            idOwner=other_user.idUser,
            visibility=PlaylistVisibility.PUBLIC,
        ),
        Playlist(
            name="Private Playlist",
            idGenre=sample_genre.idGenre,
            idOwner=other_user.idUser,
            visibility=PlaylistVisibility.PRIVATE,
        ),
    ]
    db.add_all(playlists)
    await db.commit()
    for p in playlists:
        await db.refresh(p)
    return playlists


@pytest_asyncio.fixture
async def sample_track(db: AsyncSession):
    track = Track(
        title="Imagine",
        youtubeLink="https://www.youtube.com/watch?v=voJzf0P6YPE",
    )
    db.add(track)
    await db.commit()
    await db.refresh(track)
    return track


# ---------------------------------------------------------------------------
# Happy path — admin
# ---------------------------------------------------------------------------


async def test_admin_sees_all_playlists_including_private(
    db: AsyncSession, admin_user, sample_playlists
):
    async with build_client(db, admin_user) as client:
        response = await client.get("/admin/playlists/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    visibilities = {p["visibility"] for p in data}
    assert "PRIVATE" in visibilities
    assert "PUBLIC" in visibilities


async def test_admin_can_edit_any_playlist(
    db: AsyncSession, admin_user, sample_playlists
):
    private_playlist = sample_playlists[1]
    async with build_client(db, admin_user) as client:
        response = await client.patch(
            f"/admin/playlists/{private_playlist.idPlaylist}",
            json={"name": "Renamed by Admin"},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Renamed by Admin"


async def test_admin_edit_nonexistent_playlist_returns_404(
    db: AsyncSession, admin_user
):
    async with build_client(db, admin_user) as client:
        response = await client.patch("/admin/playlists/9999", json={"name": "X"})
    assert response.status_code == 404


async def test_admin_can_delete_any_playlist(
    db: AsyncSession, admin_user, sample_playlists
):
    async with build_client(db, admin_user) as client:
        response = await client.delete(
            f"/admin/playlists/{sample_playlists[0].idPlaylist}"
        )

    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()


async def test_admin_delete_nonexistent_playlist_returns_404(
    db: AsyncSession, admin_user
):
    async with build_client(db, admin_user) as client:
        response = await client.delete("/admin/playlists/9999")
    assert response.status_code == 404


async def test_admin_can_get_tracks_of_private_playlist(
    db: AsyncSession, admin_user, sample_playlists, sample_track
):
    private_playlist = sample_playlists[1]
    tp = TrackPlaylist(
        idPlaylist=private_playlist.idPlaylist, idTrack=sample_track.idTrack
    )
    db.add(tp)
    await db.commit()

    async with build_client(db, admin_user) as client:
        response = await client.get(
            f"/admin/playlists/{private_playlist.idPlaylist}/tracks"
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Imagine"


async def test_admin_get_tracks_nonexistent_playlist_returns_404(
    db: AsyncSession, admin_user
):
    async with build_client(db, admin_user) as client:
        response = await client.get("/admin/playlists/9999/tracks")
    assert response.status_code == 404


async def test_admin_add_track_invalid_url_returns_400(
    db: AsyncSession, admin_user, sample_playlists
):
    async with build_client(db, admin_user) as client:
        response = await client.post(
            f"/admin/playlists/{sample_playlists[0].idPlaylist}/tracks/by-url",
            json={"url": "not-a-youtube-url", "title": "Some Title"},
        )
    assert response.status_code == 400


async def test_admin_add_duplicate_track_returns_409(
    db: AsyncSession, admin_user, sample_playlists, sample_track
):
    playlist = sample_playlists[0]
    tp = TrackPlaylist(idPlaylist=playlist.idPlaylist, idTrack=sample_track.idTrack)
    db.add(tp)
    await db.commit()

    async with build_client(db, admin_user) as client:
        response = await client.post(
            f"/admin/playlists/{playlist.idPlaylist}/tracks/by-url",
            json={"url": sample_track.youtubeLink, "title": sample_track.title},
        )
    assert response.status_code == 409


async def test_admin_add_track_nonexistent_playlist_returns_404(
    db: AsyncSession, admin_user
):
    async with build_client(db, admin_user) as client:
        response = await client.post(
            "/admin/playlists/9999/tracks/by-url",
            json={"url": "https://www.youtube.com/watch?v=abc", "title": "X"},
        )
    assert response.status_code == 404


async def test_admin_can_remove_track_returns_playlist(
    db: AsyncSession, admin_user, sample_playlists, sample_track
):
    playlist = sample_playlists[0]
    tp = TrackPlaylist(idPlaylist=playlist.idPlaylist, idTrack=sample_track.idTrack)
    db.add(tp)
    await db.commit()

    async with build_client(db, admin_user) as client:
        response = await client.delete(
            f"/admin/playlists/{playlist.idPlaylist}/track/{sample_track.idTrack}"
        )

    assert response.status_code == 200
    assert response.json()["idPlaylist"] == playlist.idPlaylist


# ---------------------------------------------------------------------------
# Authorization — non-admin gets 403 on every endpoint
# ---------------------------------------------------------------------------


async def test_list_playlists_forbidden_for_regular_user(
    db: AsyncSession, regular_user, sample_playlists
):
    async with build_client(db, regular_user) as client:
        response = await client.get("/admin/playlists/")
    assert response.status_code == 403


async def test_edit_playlist_forbidden_for_regular_user(
    db: AsyncSession, regular_user, sample_playlists
):
    async with build_client(db, regular_user) as client:
        response = await client.patch(
            f"/admin/playlists/{sample_playlists[0].idPlaylist}",
            json={"name": "Hacked"},
        )
    assert response.status_code == 403


async def test_delete_playlist_forbidden_for_regular_user(
    db: AsyncSession, regular_user, sample_playlists
):
    async with build_client(db, regular_user) as client:
        response = await client.delete(
            f"/admin/playlists/{sample_playlists[0].idPlaylist}"
        )
    assert response.status_code == 403


async def test_get_tracks_forbidden_for_regular_user(
    db: AsyncSession, regular_user, sample_playlists
):
    async with build_client(db, regular_user) as client:
        response = await client.get(
            f"/admin/playlists/{sample_playlists[0].idPlaylist}/tracks"
        )
    assert response.status_code == 403


async def test_add_track_forbidden_for_regular_user(
    db: AsyncSession, regular_user, sample_playlists
):
    async with build_client(db, regular_user) as client:
        response = await client.post(
            f"/admin/playlists/{sample_playlists[0].idPlaylist}/tracks/by-url",
            json={"url": "https://www.youtube.com/watch?v=abc", "title": "X"},
        )
    assert response.status_code == 403


async def test_remove_track_forbidden_for_regular_user(
    db: AsyncSession, regular_user, sample_playlists
):
    async with build_client(db, regular_user) as client:
        response = await client.delete(
            f"/admin/playlists/{sample_playlists[0].idPlaylist}/track/1"
        )
    assert response.status_code == 403
