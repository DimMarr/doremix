import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth_middleware import get_current_user, get_current_user_id
from models import Genre, Playlist, User
from models.enums import PlaylistVisibility
from models.playlist_vote import PlaylistVote
from routes.playlists import router as playlists_router


@pytest_asyncio.fixture
async def other_user(db: AsyncSession):
    user = User(
        username="paul",
        email="paul@etu.umontpellier.fr",
        password="hashed-password",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def private_foreign_playlist(
    db: AsyncSession, other_user: User, sample_genre: Genre
):
    playlist = Playlist(
        name="Locked Playlist",
        idOwner=other_user.idUser,
        idGenre=sample_genre.idGenre,
        visibility=PlaylistVisibility.PRIVATE,
    )
    db.add(playlist)
    await db.commit()
    await db.refresh(playlist)
    return playlist


@pytest_asyncio.fixture
async def anon_client(db: AsyncSession):
    app = FastAPI()
    app.include_router(playlists_router)

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


class TestPlaylistVotes:
    @pytest.mark.asyncio
    async def test_vote_requires_authentication(self, anon_client, sample_playlist):
        response = await anon_client.put(
            f"/playlists/{sample_playlist.idPlaylist}/vote",
            json={"value": 1},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_vote_uses_visibility_filtered_lookup(
        self, client, private_foreign_playlist
    ):
        response = await client.put(
            f"/playlists/{private_foreign_playlist.idPlaylist}/vote",
            json={"value": 1},
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_cast_vote_updates_score_and_user_vote(
        self, client, db: AsyncSession, sample_playlist: Playlist, sample_user: User
    ):
        response = await client.put(
            f"/playlists/{sample_playlist.idPlaylist}/vote",
            json={"value": 1},
        )

        assert response.status_code == 200
        assert response.json() == {"score": 1, "userVote": 1}

        vote_result = await db.execute(
            select(PlaylistVote).where(
                PlaylistVote.idUser == sample_user.idUser,
                PlaylistVote.idPlaylist == sample_playlist.idPlaylist,
            )
        )
        stored_vote = vote_result.scalar_one()
        assert stored_vote.value == 1

        await db.refresh(sample_playlist)
        assert sample_playlist.vote == 1

    @pytest.mark.asyncio
    async def test_switching_vote_replaces_previous_value(
        self, client, db: AsyncSession, sample_playlist: Playlist
    ):
        await client.put(f"/playlists/{sample_playlist.idPlaylist}/vote", json={"value": 1})

        response = await client.put(
            f"/playlists/{sample_playlist.idPlaylist}/vote",
            json={"value": -1},
        )

        assert response.status_code == 200
        assert response.json() == {"score": -1, "userVote": -1}

        await db.refresh(sample_playlist)
        assert sample_playlist.vote == -1

    @pytest.mark.asyncio
    async def test_repeating_active_vote_removes_it(
        self, client, db: AsyncSession, sample_playlist: Playlist, sample_user: User
    ):
        await client.put(f"/playlists/{sample_playlist.idPlaylist}/vote", json={"value": 1})

        response = await client.put(
            f"/playlists/{sample_playlist.idPlaylist}/vote",
            json={"value": 0},
        )

        assert response.status_code == 200
        assert response.json() == {"score": 0, "userVote": None}

        vote_result = await db.execute(
            select(PlaylistVote).where(
                PlaylistVote.idUser == sample_user.idUser,
                PlaylistVote.idPlaylist == sample_playlist.idPlaylist,
            )
        )
        assert vote_result.scalar_one_or_none() is None

        await db.refresh(sample_playlist)
        assert sample_playlist.vote == 0

    @pytest.mark.asyncio
    async def test_playlist_responses_include_user_vote(
        self, client, sample_playlist: Playlist
    ):
        await client.put(f"/playlists/{sample_playlist.idPlaylist}/vote", json={"value": -1})

        detail_response = await client.get(f"/playlists/{sample_playlist.idPlaylist}")
        assert detail_response.status_code == 200
        assert detail_response.json()["userVote"] == -1
        assert detail_response.json()["vote"] == -1

        list_response = await client.get("/playlists/")
        assert list_response.status_code == 200
        matching = next(
            playlist
            for playlist in list_response.json()
            if playlist["idPlaylist"] == sample_playlist.idPlaylist
        )
        assert matching["userVote"] == -1
        assert matching["vote"] == -1
