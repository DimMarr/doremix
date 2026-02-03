import pytest
from datetime import datetime
from models import Playlist, PlaylistVisibility, User, Genre, Track, Artist
from sqlalchemy.orm import Session


@pytest.fixture
def sample_genre(db: Session):
    """Crée un genre de test."""
    genre = Genre(label="Rock")
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


@pytest.fixture
def sample_user(db: Session):
    """Crée un utilisateur de test."""
    user = User(
        email="test@example.com", password="hashed_password", username="testuser"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_artist(db: Session):
    """Crée un artiste de test."""
    artist = Artist(name="John Lennon")
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


@pytest.fixture
def sample_playlists(db: Session, sample_user, sample_genre):
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
    db.commit()

    for playlist in playlists:
        db.refresh(playlist)

    return playlists


@pytest.fixture
def sample_track(db, sample_artist):
    """Crée un track de test avec un artiste"""
    track = Track(
        title="Imagine",
        youtubeLink="https://www.youtube.com/watch?v=voJzf0P6YPE",
    )
    track.artists.append(sample_artist)
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


class TestSearch:
    """Tests pour l'endpoint de recherche /search."""

    def test_search_finds_playlists(self, client, sample_playlists):
        """Test la recherche de playlists par nom."""
        response = client.get("/search", params={"q": "Rock67"})
        assert response.status_code == 200

        data = response.json()
        assert data["playlists"][0]["name"] == "Rock67"
        assert len(data["playlists"]) == 1
        assert len(data["tracks"]) == 0

    def test_search_finds_tracks(self, client, sample_track):
        """Test la recherche de tracks par titre."""
        response = client.get("/search", params={"q": "Imagine"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["tracks"]) == 1
        assert data["tracks"][0]["title"] == "Imagine"
        assert len(data["playlists"]) == 0

    def test_search_finds_both_playlists_and_tracks(
        self, client, sample_playlists, sample_track, sample_artist, db: Session
    ):
        """Test la recherche qui trouve à la fois des playlists et des tracks."""
        track = Track(
            title="Rock67 Song",
            youtubeLink="https://www.youtube.com/watch?v=test",
        )
        track.artists.append(sample_artist)
        db.add(track)
        db.commit()

        response = client.get("/search", params={"q": "Rock67"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["playlists"]) >= 1
        assert len(data["tracks"]) >= 1

    def test_search_empty_results(self, client):
        """Test la recherche sans résultats."""
        response = client.get("/search", params={"q": "NonExistentSearchTerm123456"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["playlists"]) == 0
        assert len(data["tracks"]) == 0

    def test_search_case_insensitive(self, client, sample_playlists):
        """Test que la recherche est insensible à la casse."""
        response = client.get("/search", params={"q": "rock67"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["playlists"]) >= 1

    def test_search_partial_match(self, client, sample_playlists):
        """Test la recherche avec correspondance partielle."""
        response = client.get("/search", params={"q": "Rock"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["playlists"]) >= 1

    def test_search_with_minimum_query_length(self, client):
        """Test la recherche avec la longueur minimale de query."""
        response = client.get("/search", params={"q": "ab"})
        assert response.status_code == 200

    def test_search_with_query_too_short(self, client):
        """Test la recherche avec une query trop courte."""
        response = client.get("/search", params={"q": "a"})
        assert response.status_code == 422

    def test_search_without_query_parameter(self, client):
        """Test la recherche sans paramètre de query."""
        response = client.get("/search")
        assert response.status_code == 422

    def test_search_with_special_characters(
        self, client, db: Session, sample_user, sample_genre
    ):
        """Test la recherche avec des caractères spéciaux."""
        playlist = Playlist(
            name="Rock & Roll",
            idGenre=sample_genre.idGenre,
            idOwner=sample_user.idUser,
            visibility=PlaylistVisibility.PUBLIC,
        )
        db.add(playlist)
        db.commit()

        response = client.get("/search", params={"q": "Rock & Roll"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["playlists"]) >= 1

    def test_search_returns_correct_structure(
        self, client, sample_playlists, sample_track
    ):
        """Test que la recherche retourne la structure correcte."""
        response = client.get("/search", params={"q": "Rock"})
        assert response.status_code == 200

        data = response.json()
        assert "playlists" in data
        assert "tracks" in data
        assert isinstance(data["playlists"], list)
        assert isinstance(data["tracks"], list)
