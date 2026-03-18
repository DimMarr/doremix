"""
Tests for admin playlist management endpoints: /admin/playlists/*
Follows the pattern established in test_moderation.py.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

import middleware.auth_middleware as auth_middleware
from database import Base, get_db
from middleware.auth_middleware import get_current_user_id
from routes.admin_playlists import router as admin_playlists_router
from models import User, Genre
from models.enums import PlaylistVisibility
from models.playlist import Playlist
from models.track import Track
from models.track_playlist import TrackPlaylist


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def create_user(db: Session, email: str, username: str, id_role: int) -> User:
    user = User(
        email=email,
        username=username,
        password="hashed-password",
        idRole=id_role,
        isVerified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_actor(client: TestClient, monkeypatch: pytest.MonkeyPatch, actor: User):
    """Authenticates the client as the given user.
    Must patch auth_middleware.get_current_user directly because require_role
    calls it as a plain function, not via FastAPI DI.
    """
    client.app.dependency_overrides[get_current_user_id] = lambda: actor.idUser
    monkeypatch.setattr(
        auth_middleware, "get_current_user", lambda request, _actor=actor: _actor
    )


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def admin_client(db: Session):
    app = FastAPI()
    app.include_router(admin_playlists_router)

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_genre(db: Session):
    genre = Genre(label="Rock")
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


@pytest.fixture
def admin_user(db: Session):
    return create_user(db, "admin@test.com", "admin", 3)


@pytest.fixture
def regular_user(db: Session):
    return create_user(db, "regular@test.com", "regular", 1)


@pytest.fixture
def other_user(db: Session):
    """Another regular user who owns playlists."""
    return create_user(db, "other@test.com", "other", 1)


@pytest.fixture
def sample_playlists(db: Session, other_user, sample_genre):
    """Creates playlists owned by another user, including PRIVATE ones."""
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
    db.commit()
    for p in playlists:
        db.refresh(p)
    return playlists


@pytest.fixture
def sample_track(db: Session):
    track = Track(
        title="Imagine",
        youtubeLink="https://www.youtube.com/watch?v=voJzf0P6YPE",
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


# ---------------------------------------------------------------------------
# Happy path — admin
# ---------------------------------------------------------------------------


def test_admin_sees_all_playlists_including_private(
    admin_client, db, monkeypatch, admin_user, sample_playlists
):
    """Admin GET /admin/playlists/ returns all playlists including PRIVATE ones."""
    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.get("/admin/playlists/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    visibilities = {p["visibility"] for p in data}
    assert "PRIVATE" in visibilities
    assert "PUBLIC" in visibilities


def test_admin_can_edit_any_playlist(
    admin_client, db, monkeypatch, admin_user, sample_playlists
):
    """Admin PATCH /admin/playlists/{id} updates a PRIVATE playlist owned by another user."""
    private_playlist = sample_playlists[1]
    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.patch(
        f"/admin/playlists/{private_playlist.idPlaylist}",
        json={"name": "Renamed by Admin"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Renamed by Admin"


def test_admin_edit_nonexistent_playlist_returns_404(
    admin_client, db, monkeypatch, admin_user
):
    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.patch("/admin/playlists/9999", json={"name": "X"})
    assert response.status_code == 404


def test_admin_can_delete_any_playlist(
    admin_client, db, monkeypatch, admin_user, sample_playlists
):
    """Admin DELETE /admin/playlists/{id} deletes a playlist owned by another user."""
    set_actor(admin_client, monkeypatch, admin_user)
    playlist_id = sample_playlists[0].idPlaylist
    response = admin_client.delete(f"/admin/playlists/{playlist_id}")

    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()


def test_admin_delete_nonexistent_playlist_returns_404(
    admin_client, db, monkeypatch, admin_user
):
    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.delete("/admin/playlists/9999")
    assert response.status_code == 404


def test_admin_can_get_tracks_of_private_playlist(
    admin_client, db, monkeypatch, admin_user, sample_playlists, sample_track
):
    """Admin GET /admin/playlists/{id}/tracks returns tracks for a PRIVATE playlist."""
    private_playlist = sample_playlists[1]
    tp = TrackPlaylist(
        idPlaylist=private_playlist.idPlaylist, idTrack=sample_track.idTrack
    )
    db.add(tp)
    db.commit()

    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.get(
        f"/admin/playlists/{private_playlist.idPlaylist}/tracks"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Imagine"


def test_admin_get_tracks_nonexistent_playlist_returns_404(
    admin_client, db, monkeypatch, admin_user
):
    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.get("/admin/playlists/9999/tracks")
    assert response.status_code == 404


def test_admin_add_track_invalid_url_returns_400(
    admin_client, db, monkeypatch, admin_user, sample_playlists
):
    """Admin POST /admin/playlists/{id}/tracks/by-url with invalid URL returns 400."""
    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.post(
        f"/admin/playlists/{sample_playlists[0].idPlaylist}/tracks/by-url",
        json={"url": "not-a-youtube-url", "title": "Some Title"},
    )
    assert response.status_code == 400


def test_admin_add_duplicate_track_returns_409(
    admin_client, db, monkeypatch, admin_user, sample_playlists, sample_track
):
    """Admin POST adding a track already in the playlist returns 409."""
    playlist = sample_playlists[0]
    tp = TrackPlaylist(idPlaylist=playlist.idPlaylist, idTrack=sample_track.idTrack)
    db.add(tp)
    db.commit()

    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.post(
        f"/admin/playlists/{playlist.idPlaylist}/tracks/by-url",
        json={"url": sample_track.youtubeLink, "title": sample_track.title},
    )
    assert response.status_code == 409


def test_admin_add_track_nonexistent_playlist_returns_404(
    admin_client, db, monkeypatch, admin_user
):
    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.post(
        "/admin/playlists/9999/tracks/by-url",
        json={"url": "https://www.youtube.com/watch?v=abc", "title": "X"},
    )
    assert response.status_code == 404


def test_admin_can_remove_track_returns_playlist(
    admin_client, db, monkeypatch, admin_user, sample_playlists, sample_track
):
    """Admin DELETE /admin/playlists/{id}/track/{track_id} removes track, returns playlist."""
    playlist = sample_playlists[0]
    tp = TrackPlaylist(idPlaylist=playlist.idPlaylist, idTrack=sample_track.idTrack)
    db.add(tp)
    db.commit()

    set_actor(admin_client, monkeypatch, admin_user)
    response = admin_client.delete(
        f"/admin/playlists/{playlist.idPlaylist}/track/{sample_track.idTrack}"
    )

    assert response.status_code == 200
    assert response.json()["idPlaylist"] == playlist.idPlaylist


# ---------------------------------------------------------------------------
# Authorization — non-admin gets 403 on every endpoint
# ---------------------------------------------------------------------------


def test_list_playlists_forbidden_for_regular_user(
    admin_client, db, monkeypatch, regular_user, sample_playlists
):
    set_actor(admin_client, monkeypatch, regular_user)
    response = admin_client.get("/admin/playlists/")
    assert response.status_code == 403


def test_edit_playlist_forbidden_for_regular_user(
    admin_client, db, monkeypatch, regular_user, sample_playlists
):
    set_actor(admin_client, monkeypatch, regular_user)
    response = admin_client.patch(
        f"/admin/playlists/{sample_playlists[0].idPlaylist}",
        json={"name": "Hacked"},
    )
    assert response.status_code == 403


def test_delete_playlist_forbidden_for_regular_user(
    admin_client, db, monkeypatch, regular_user, sample_playlists
):
    set_actor(admin_client, monkeypatch, regular_user)
    response = admin_client.delete(f"/admin/playlists/{sample_playlists[0].idPlaylist}")
    assert response.status_code == 403


def test_get_tracks_forbidden_for_regular_user(
    admin_client, db, monkeypatch, regular_user, sample_playlists
):
    set_actor(admin_client, monkeypatch, regular_user)
    response = admin_client.get(
        f"/admin/playlists/{sample_playlists[0].idPlaylist}/tracks"
    )
    assert response.status_code == 403


def test_add_track_forbidden_for_regular_user(
    admin_client, db, monkeypatch, regular_user, sample_playlists
):
    set_actor(admin_client, monkeypatch, regular_user)
    response = admin_client.post(
        f"/admin/playlists/{sample_playlists[0].idPlaylist}/tracks/by-url",
        json={"url": "https://www.youtube.com/watch?v=abc", "title": "X"},
    )
    assert response.status_code == 403


def test_remove_track_forbidden_for_regular_user(
    admin_client, db, monkeypatch, regular_user, sample_playlists
):
    set_actor(admin_client, monkeypatch, regular_user)
    response = admin_client.delete(
        f"/admin/playlists/{sample_playlists[0].idPlaylist}/track/1"
    )
    assert response.status_code == 403
