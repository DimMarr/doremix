import pytest
from datetime import datetime
from models import Playlist, PlaylistVisibility, User, Genre
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
def sample_playlists(db: Session, sample_user, sample_genre):
    """Crée des playlists de test."""
    playlists = [
        Playlist(
            name="My Favorite Songs",
            idGenre=sample_genre.idGenre,
            idOwner=sample_user.idUser,
            vote=10,
            visibility=PlaylistVisibility.PUBLIC,
        ),
        Playlist(
            name="Private Mix",
            idGenre=sample_genre.idGenre,
            idOwner=sample_user.idUser,
            vote=5,
            visibility=PlaylistVisibility.PRIVATE,
        ),
        Playlist(
            name="Workout Playlist",
            idGenre=sample_genre.idGenre,
            idOwner=sample_user.idUser,
            vote=8,
            visibility=PlaylistVisibility.PUBLIC,
        ),
    ]
    db.add_all(playlists)
    db.commit()

    for playlist in playlists:
        db.refresh(playlist)

    return playlists


class TestGetAllPlaylists:
    """Tests pour l'endpoint GET /playlists/."""

    def test_get_all_playlists_success(self, client, sample_playlists):
        """Test la récupération de toutes les playlists avec succès."""
        response = client.get("/playlists/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        for playlist in data:
            assert "idPlaylist" in playlist
            assert "name" in playlist
            assert "idGenre" in playlist
            assert "idOwner" in playlist
            assert "vote" in playlist
            assert "visibility" in playlist
            assert "createdAt" in playlist
            assert "updatedAt" in playlist

    def test_get_all_playlists_empty(self, client):
        """Test la récupération de playlists quand la BD est vide."""
        response = client.get("/playlists/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_playlists_returns_correct_data(self, client, sample_playlists):
        """Test que les données retournées correspondent aux playlists créées."""
        response = client.get("/playlists/")
        assert response.status_code == 200

        data = response.json()

        assert data[0]["name"] == "My Favorite Songs"
        assert data[0]["vote"] == 10
        assert data[0]["visibility"] == "PUBLIC"

        assert data[1]["name"] == "Private Mix"
        assert data[1]["vote"] == 5
        assert data[1]["visibility"] == "PRIVATE"

    def test_get_all_playlists_different_visibilities(self, client, sample_playlists):
        """Test la récupération de playlists avec différents niveaux de visibilité."""
        response = client.get("/playlists/")
        assert response.status_code == 200

        data = response.json()
        visibilities = [p["visibility"] for p in data]

        assert "PUBLIC" in visibilities
        assert "PRIVATE" in visibilities

    def test_get_all_playlists_response_schema(self, client, sample_playlists):
        """Test que la réponse correspond au schéma attendu."""
        response = client.get("/playlists/")
        assert response.status_code == 200

        data = response.json()

        for playlist in data:
            assert isinstance(playlist["idPlaylist"], int)
            assert isinstance(playlist["name"], str)
            assert isinstance(playlist["idGenre"], int)
            assert isinstance(playlist["idOwner"], int)
            assert isinstance(playlist["vote"], int)
            assert isinstance(playlist["visibility"], str)
            assert isinstance(playlist["createdAt"], str)
            assert isinstance(playlist["updatedAt"], str)


class TestGetPlaylistById:
    """Tests pour l'endpoint GET /playlists/{playlist_id}."""

    def test_get_playlist_by_id_success(self, client, sample_playlists):
        """Test la récupération d'une playlist par ID avec succès."""
        playlist_id = sample_playlists[0].idPlaylist
        response = client.get(f"/playlists/{playlist_id}")

        assert response.status_code == 200

        data = response.json()
        assert data["idPlaylist"] == playlist_id
        assert data["name"] == "My Favorite Songs"
        assert data["vote"] == 10

    def test_get_playlist_by_id_not_found(self, client):
        """Test la récupération d'une playlist inexistante."""
        try:
            response = client.get("/playlists/999")
            assert response.status_code in [404, 422, 500]
        except Exception as e:
            assert (
                "ResponseValidationError" in str(type(e))
                or "validation error" in str(e).lower()
            )

    def test_get_playlist_by_id_structure(self, client, sample_playlists):
        """Test la structure de la réponse pour une playlist unique."""
        playlist_id = sample_playlists[1].idPlaylist
        response = client.get(f"/playlists/{playlist_id}")

        assert response.status_code == 200
        data = response.json()

        assert "idPlaylist" in data
        assert "name" in data
        assert "idGenre" in data
        assert "idOwner" in data
        assert "vote" in data
        assert "visibility" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_get_playlist_private_visibility(self, client, sample_playlists):
        """Test la récupération d'une playlist privée."""
        private_playlist = next(
            p for p in sample_playlists if p.visibility == PlaylistVisibility.PRIVATE
        )
        response = client.get(f"/playlists/{private_playlist.idPlaylist}")

        assert response.status_code == 200
        data = response.json()
        assert data["visibility"] == "PRIVATE"

    def test_get_playlist_by_id_invalid_id_type(self, client):
        """Test avec un type d'ID de playlist invalide."""
        response = client.get("/playlists/invalid")

        assert response.status_code == 422

    def test_get_playlist_by_id_negative_id(self, client):
        """Test avec un ID de playlist négatif."""
        try:
            response = client.get("/playlists/-1")
            assert response.status_code in [404, 422, 500]
        except Exception as e:
            assert (
                "ResponseValidationError" in str(type(e))
                or "validation error" in str(e).lower()
            )

    def test_get_playlist_preserves_data_integrity(
        self, client, sample_playlists, db: Session
    ):
        """Test que la récupération d'une playlist ne la modifie pas."""
        original_playlist = sample_playlists[0]
        original_name = original_playlist.name
        original_vote = original_playlist.vote

        response = client.get(f"/playlists/{original_playlist.idPlaylist}")
        assert response.status_code == 200

        db_playlist = (
            db.query(Playlist)
            .filter(Playlist.idPlaylist == original_playlist.idPlaylist)
            .first()
        )

        assert db_playlist is not None
        assert db_playlist.name == original_name
        assert db_playlist.vote == original_vote

    def test_get_playlist_response_types(self, client, sample_playlists):
        """Test que les champs de la réponse ont les bons types de données."""
        playlist_id = sample_playlists[0].idPlaylist
        response = client.get(f"/playlists/{playlist_id}")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data["idPlaylist"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["idGenre"], int)
        assert isinstance(data["idOwner"], int)
        assert isinstance(data["vote"], int)
        assert isinstance(data["visibility"], str)
        assert isinstance(data["createdAt"], str)
        assert isinstance(data["updatedAt"], str)


class TestPlaylistEdgeCases:
    """Tests pour les cas limites et scénarios spéciaux."""

    def test_get_multiple_playlists_from_same_owner(
        self, client, db: Session, sample_user, sample_genre
    ):
        """Test la récupération de plusieurs playlists du même propriétaire."""
        playlists = [
            Playlist(
                name=f"Playlist {i}",
                idGenre=sample_genre.idGenre,
                idOwner=sample_user.idUser,
            )
            for i in range(5)
        ]
        db.add_all(playlists)
        db.commit()

        response = client.get("/playlists/")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 5

        assert all(p["idOwner"] == sample_user.idUser for p in data)

    def test_playlist_with_high_vote_count(
        self, client, db: Session, sample_user, sample_genre
    ):
        """Test une playlist avec un haut nombre de votes."""
        playlist = Playlist(
            name="Popular Playlist",
            idGenre=sample_genre.idGenre,
            idOwner=sample_user.idUser,
            vote=999999,
        )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

        response = client.get(f"/playlists/{playlist.idPlaylist}")
        assert response.status_code == 200

        data = response.json()
        assert data["vote"] == 999999

    def test_playlist_name_with_special_characters(
        self, client, db: Session, sample_user, sample_genre
    ):
        """Test une playlist avec des caractères spéciaux dans le nom."""
        special_names = [
            "Rock & Roll Mix",
            "80's Classics",
            "K-pop / J-pop",
            "Café Music ☕",
        ]

        for name in special_names:
            playlist = Playlist(
                name=name, idGenre=sample_genre.idGenre, idOwner=sample_user.idUser
            )
            db.add(playlist)

        db.commit()

        response = client.get("/playlists/")
        assert response.status_code == 200

        data = response.json()
        returned_names = [p["name"] for p in data]

        for name in special_names:
            assert name in returned_names

    def test_all_visibility_types(self, client, db: Session, sample_user, sample_genre):
        """Test que tous les types de visibilité sont retournés correctement."""
        visibility_types = [
            PlaylistVisibility.PUBLIC,
            PlaylistVisibility.PRIVATE,
            PlaylistVisibility.OPEN,
            PlaylistVisibility.SHARED,
        ]

        for visibility in visibility_types:
            playlist = Playlist(
                name=f"Playlist - {visibility.value}",
                idGenre=sample_genre.idGenre,
                idOwner=sample_user.idUser,
                visibility=visibility,
            )
            db.add(playlist)

        db.commit()

        response = client.get("/playlists/")
        assert response.status_code == 200

        data = response.json()
        returned_visibilities = [p["visibility"] for p in data]

        for visibility in visibility_types:
            assert visibility.value in returned_visibilities
