import pytest
from models import Playlist, PlaylistVisibility, Track, Artist
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def sample_artist(db: AsyncSession):
    """Crée un artiste de test."""
    artist = Artist(name="John Lennon")
    db.add(artist)
    await db.commit()
    await db.refresh(artist)
    return artist


@pytest.fixture
async def sample_playlists(db: AsyncSession, sample_user, sample_genre):
    """Crée des playlists de test."""
    playlists = [
        Playlist(
            name="Rock67",
            idGenre=sample_genre.idGenre,
            idOwner=sample_user.idUser,
            vote=10,
            visibility=PlaylistVisibility.PUBLIC,
        )
    ]
    db.add_all(playlists)
    await db.commit()

    for playlist in playlists:
        await db.refresh(playlist)

    return playlists


@pytest.fixture
async def sample_track(db, sample_artist):
    """Crée un track de test avec un artiste"""
    track = Track(
        title="Imagine",
        youtubeLink="https://www.youtube.com/watch?v=voJzf0P6YPE",
    )
    track.artists.append(sample_artist)
    db.add(track)
    await db.commit()
    await db.refresh(track)
    return track


class TestSearch:
    """Tests pour l'endpoint de recherche /search."""

    @pytest.mark.asyncio
    async def test_search_finds_playlists(self, client, sample_playlists):
        """Test la recherche de playlists par nom."""
        response = await client.get("/search", params={"q": "Rock67"})
        assert response.status_code == 200

        data = response.json()
        assert data["playlists"][0]["name"] == "Rock67"
        assert len(data["playlists"]) == 1
        assert len(data["tracks"]) == 0

    @pytest.mark.asyncio
    async def test_search_finds_tracks(self, client, sample_track):
        """Test la recherche de tracks par titre."""
        response = await client.get("/search", params={"q": "Imagine"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["tracks"]) == 1
        assert data["tracks"][0]["title"] == "Imagine"
        assert len(data["playlists"]) == 0

    @pytest.mark.asyncio
    async def test_search_finds_both_playlists_and_tracks(
        self, client, sample_playlists, sample_track, sample_artist, db: AsyncSession
    ):
        """Test la recherche qui trouve à la fois des playlists et des tracks."""
        track = Track(
            title="Rock67 Song",
            youtubeLink="https://www.youtube.com/watch?v=test",
        )
        track.artists.append(sample_artist)
        db.add(track)
        await db.commit()

        response = await client.get("/search", params={"q": "Rock67"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["playlists"]) >= 1
        assert len(data["tracks"]) >= 1

    @pytest.mark.asyncio
    async def test_search_empty_results(self, client):
        """Test la recherche sans résultats."""
        response = await client.get(
            "/search", params={"q": "NonExistentSearchTerm123456"}
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["playlists"]) == 0
        assert len(data["tracks"]) == 0

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, client, sample_playlists):
        """Test que la recherche est insensible à la casse."""
        response = await client.get("/search", params={"q": "rock67"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["playlists"]) >= 1

    @pytest.mark.asyncio
    async def test_search_partial_match(self, client, sample_playlists):
        """Test la recherche avec correspondance partielle."""
        response = await client.get("/search", params={"q": "Rock"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["playlists"]) >= 1

    @pytest.mark.asyncio
    async def test_search_with_minimum_query_length(self, client):
        """Test la recherche avec la longueur minimale de query."""
        response = await client.get("/search", params={"q": "ab"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_with_query_too_short(self, client):
        """Test la recherche avec une query trop courte."""
        response = await client.get("/search", params={"q": "a"})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_without_query_parameter(self, client):
        """Test la recherche sans paramètre de query."""
        response = await client.get("/search")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_with_special_characters(
        self, client, db: AsyncSession, sample_user, sample_genre
    ):
        """Test la recherche avec des caractères spéciaux."""
        playlist = Playlist(
            name="Rock & Roll",
            idGenre=sample_genre.idGenre,
            idOwner=sample_user.idUser,
            visibility=PlaylistVisibility.PUBLIC,
        )
        db.add(playlist)
        await db.commit()

        response = await client.get("/search", params={"q": "Rock & Roll"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["playlists"]) >= 1

    @pytest.mark.asyncio
    async def test_search_returns_correct_structure(
        self, client, sample_playlists, sample_track
    ):
        """Test que la recherche retourne la structure correcte."""
        response = await client.get("/search", params={"q": "Rock"})
        assert response.status_code == 200

        data = response.json()
        assert "playlists" in data
        assert "tracks" in data
        assert isinstance(data["playlists"], list)
        assert isinstance(data["tracks"], list)
