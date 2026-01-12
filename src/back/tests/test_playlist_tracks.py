"""
Tests pour l'ajout et la suppression de tracks dans une playlist
"""

import pytest
from sqlalchemy.orm import Session

from models import User, Playlist, Track, Genre


@pytest.fixture
def sample_user(db):
    """Crée un utilisateur de test"""
    user = User(
        username="testuser", email="test@example.com", password="hashed_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_playlist(db, sample_user):
    """Crée une playlist de test"""
    playlist = Playlist(name="Ma Playlist", idOwner=sample_user.idUser, idGenre=1)
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


@pytest.fixture
def sample_genre(db):
    """Crée un genre de test"""
    genre = Genre(label="Rock")
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


@pytest.fixture
def sample_track(db):
    """Crée un track de test"""
    track = Track(
        title="Imagine",
        youtubeLink="https://www.youtube.com/watch?v=voJzf0P6YPE",
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


@pytest.fixture
def sample_track_2(db):
    """Crée un deuxième track de test"""
    track = Track(
        title="Bohemian Rhapsody",
        youtubeLink="https://www.youtube.com/watch?v=fJ9rUzIMt7o",
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


class TestPlaylistTrackOperations:
    """Suite de tests pour les opérations de tracks dans une playlist"""

    def test_add_track_to_playlist_success(self, client, sample_playlist, sample_track):
        """Test l'ajout d'un track à une playlist avec succès"""
        response = client.post(
            f"/playlists/{sample_playlist.idPlaylist}/track",
            params={
                "title": sample_track.title,
                "youtubeLink": sample_track.youtubeLink,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_track.title

    def test_add_multiple_tracks_to_playlist(
        self, client, sample_playlist, sample_track, sample_track_2
    ):
        """Test l'ajout de plusieurs tracks à une playlist"""
        # Ajouter le premier track
        response1 = client.post(
            f"/playlists/{sample_playlist.idPlaylist}/track",
            params={
                "title": sample_track.title,
                "youtubeLink": sample_track.youtubeLink,
            },
        )
        assert response1.status_code == 200

        # Ajouter le deuxième track
        response2 = client.post(
            f"/playlists/{sample_playlist.idPlaylist}/track",
            params={
                "title": sample_track_2.title,
                "youtubeLink": sample_track_2.youtubeLink,
            },
        )
        assert response2.status_code == 200

        # Vérifier que les deux tracks sont dans la playlist
        get_response = client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        assert get_response.status_code == 200
        tracks = get_response.json()
        assert len(tracks) >= 2

    def test_add_track_to_nonexistent_playlist(self, client, sample_track):
        """Test l'ajout d'un track à une playlist inexistante"""
        response = client.post(
            "/playlists/9999/track",
            params={
                "title": sample_track.title,
                "youtubeLink": sample_track.youtubeLink,
            },
        )

        # Doit retourner une erreur 404 ou 422
        assert response.status_code in [404, 422]

    def test_remove_track_from_playlist_success(
        self, client, sample_playlist, sample_track
    ):
        """Test la suppression d'un track d'une playlist avec succès"""
        # Ajouter le track d'abord
        add_response = client.post(
            f"/playlists/{sample_playlist.idPlaylist}/track",
            params={
                "title": sample_track.title,
                "youtubeLink": sample_track.youtubeLink,
            },
        )
        assert add_response.status_code == 200

        # Récupérer l'ID du track ajouté
        track_data = add_response.json()
        track_id = track_data.get("idTrack") or track_data.get("id")

        # Supprimer le track
        delete_response = client.delete(
            f"/playlists/{sample_playlist.idPlaylist}/track/{track_id}"
        )
        assert delete_response.status_code == 200

        # Vérifier que le track a été supprimé
        get_response = client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        assert get_response.status_code == 200
        tracks = get_response.json()
        track_ids = [t.get("idTrack") or t.get("id") for t in tracks]
        assert track_id not in track_ids

    def test_remove_nonexistent_track_from_playlist(self, client, sample_playlist):
        """Test la suppression d'un track inexistant"""
        response = client.delete(f"/playlists/{sample_playlist.idPlaylist}/track/9999")

        # Doit retourner une erreur
        assert response.status_code in [404, 422]

    def test_remove_track_from_nonexistent_playlist(self, client):
        """Test la suppression d'un track d'une playlist inexistante"""
        response = client.delete("/playlists/9999/track/9999")

        # Doit retourner une erreur
        assert response.status_code in [404, 422]

    def test_get_playlist_tracks_empty(self, client, sample_playlist):
        """Test la récupération des tracks d'une playlist vide"""
        response = client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")

        assert response.status_code == 200
        tracks = response.json()
        assert isinstance(tracks, list)
        assert len(tracks) == 0

    def test_get_playlist_tracks_with_multiple_tracks(
        self, client, sample_playlist, sample_track, sample_track_2
    ):
        """Test la récupération des tracks d'une playlist avec plusieurs tracks"""
        # Ajouter les tracks
        client.post(
            f"/playlists/{sample_playlist.idPlaylist}/track",
            params={
                "title": sample_track.title,
                "youtubeLink": sample_track.youtubeLink,
            },
        )
        client.post(
            f"/playlists/{sample_playlist.idPlaylist}/track",
            params={
                "title": sample_track_2.title,
                "youtubeLink": sample_track_2.youtubeLink,
            },
        )

        # Récupérer les tracks
        response = client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        assert response.status_code == 200
        tracks = response.json()
        assert len(tracks) >= 2

    def test_playlist_operations_order(
        self, client, sample_playlist, sample_track, sample_track_2
    ):
        """Test l'ordre des opérations: ajout, lecture, suppression"""
        # Vérifier que la playlist est vide au départ
        response = client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        assert response.status_code == 200
        assert len(response.json()) == 0

        # Ajouter un track
        add_response = client.post(
            f"/playlists/{sample_playlist.idPlaylist}/track",
            params={
                "title": sample_track.title,
                "youtubeLink": sample_track.youtubeLink,
            },
        )
        assert add_response.status_code == 200
        track_id = add_response.json().get("idTrack") or add_response.json().get("id")

        # Vérifier qu'il est présent
        response = client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        assert len(response.json()) == 1

        # Supprimer le track
        delete_response = client.delete(
            f"/playlists/{sample_playlist.idPlaylist}/track/{track_id}"
        )
        assert delete_response.status_code == 200

        # Vérifier qu'il est supprimé
        response = client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        assert len(response.json()) == 0

    def test_track_order_after_add_remove(
        self, client, sample_playlist, sample_track, sample_track_2
    ):
        """Test que l'ordre des tracks est maintenu après ajout/suppression"""
        # Ajouter track 1
        add1 = client.post(
            f"/playlists/{sample_playlist.idPlaylist}/track",
            params={
                "title": sample_track.title,
                "youtubeLink": sample_track.youtubeLink,
            },
        )
        track1_id = add1.json().get("idTrack") or add1.json().get("id")

        # Ajouter track 2
        add2 = client.post(
            f"/playlists/{sample_playlist.idPlaylist}/track",
            params={
                "title": sample_track_2.title,
                "youtubeLink": sample_track_2.youtubeLink,
            },
        )
        track2_id = add2.json().get("idTrack") or add2.json().get("id")

        # Vérifier l'ordre
        get_response = client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        tracks = get_response.json()
        track_ids = [t.get("idTrack") or t.get("id") for t in tracks]

        # Vérifier que track 1 vient avant track 2
        if len(tracks) >= 2 and track1_id in track_ids and track2_id in track_ids:
            assert track_ids.index(track1_id) < track_ids.index(track2_id)

        # Supprimer track 1
        client.delete(f"/playlists/{sample_playlist.idPlaylist}/track/{track1_id}")

        # Vérifier que track 2 est toujours présent
        get_response = client.get(f"/playlists/{sample_playlist.idPlaylist}/tracks")
        tracks = get_response.json()
        track_ids = [t.get("idTrack") or t.get("id") for t in tracks]
        assert track2_id in track_ids
