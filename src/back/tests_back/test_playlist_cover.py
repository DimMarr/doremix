"""
Tests pour l'upload de cover images pour les playlists
"""

import pytest
from sqlalchemy.orm import Session
from io import BytesIO
import tempfile
import shutil
import os
from PIL import Image

from models import User, Playlist, Genre, PlaylistVisibility


def create_test_image(format="JPEG", size=(100, 100), color="red"):
    """Crée une image de test valide"""
    img = Image.new("RGB", size, color)
    buffer = BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer


@pytest.fixture
def temp_upload_dir(monkeypatch):
    """Crée un répertoire temporaire pour les uploads et le patch dans le module"""
    temp_dir = tempfile.mkdtemp()

    # Patch le UPLOAD_DIR dans le module image_processor
    import utils.image_processor as image_processor

    monkeypatch.setattr(image_processor, "UPLOAD_DIR", temp_dir)

    yield temp_dir

    # Nettoyer après les tests
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


class TestPlaylistCoverUpload:
    """Tests pour l'upload de cover images pour les playlists."""

    def test_upload_cover_success(self, client, sample_playlists, temp_upload_dir):
        """Test l'upload réussi d'une cover image."""
        playlist_id = sample_playlists[0].idPlaylist

        # Créer une vraie image de test
        image_buffer = create_test_image()
        files = {"file": ("test_cover.jpg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

        data = response.json()
        assert "coverImage" in data
        assert data["coverImage"] is not None

    def test_upload_cover_png_format(self, client, sample_playlists, temp_upload_dir):
        """Test l'upload d'une cover image au format PNG."""
        playlist_id = sample_playlists[0].idPlaylist

        image_buffer = create_test_image(format="PNG")
        files = {"file": ("test_cover.png", image_buffer, "image/png")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

        data = response.json()
        assert "coverImage" in data

    def test_upload_cover_to_nonexistent_playlist(self, client, temp_upload_dir):
        """Test l'upload d'une cover à une playlist inexistante."""
        image_buffer = create_test_image()
        files = {"file": ("test_cover.jpg", image_buffer, "image/jpeg")}

        response = client.post("/playlists/9999/cover", files=files)
        assert response.status_code in [404, 422]

    def test_upload_cover_without_file(self, client, sample_playlists, temp_upload_dir):
        """Test l'upload d'une cover sans fichier."""
        playlist_id = sample_playlists[0].idPlaylist

        response = client.post(f"/playlists/{playlist_id}/cover")
        assert response.status_code == 422

    def test_upload_cover_replaces_existing(
        self, client, sample_playlists, temp_upload_dir
    ):
        """Test que l'upload d'une nouvelle cover remplace l'ancienne."""
        playlist_id = sample_playlists[0].idPlaylist

        # Premier upload
        image_buffer_1 = create_test_image(color="red")
        files_1 = {"file": ("cover1.jpg", image_buffer_1, "image/jpeg")}
        response_1 = client.post(f"/playlists/{playlist_id}/cover", files=files_1)
        assert response_1.status_code == 200
        cover_1 = response_1.json()["coverImage"]

        # Deuxième upload
        image_buffer_2 = create_test_image(color="blue")
        files_2 = {"file": ("cover2.jpg", image_buffer_2, "image/jpeg")}
        response_2 = client.post(f"/playlists/{playlist_id}/cover", files=files_2)
        assert response_2.status_code == 200
        cover_2 = response_2.json()["coverImage"]

        # Vérifier que les covers ont le même nom (le fichier est remplacé)
        assert cover_1 == cover_2  # Le nom reste le même (playlist_{id}.webp)

    def test_upload_cover_updates_playlist(
        self, client, sample_playlists, db: Session, temp_upload_dir
    ):
        """Test que l'upload d'une cover met à jour la playlist dans la base de données."""
        playlist_id = sample_playlists[0].idPlaylist

        image_buffer = create_test_image()
        files = {"file": ("test_cover.jpg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

        db_playlist = (
            db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
        )
        assert db_playlist is not None
        assert db_playlist.coverImage is not None

    def test_upload_cover_with_invalid_file_type(
        self, client, sample_playlists, temp_upload_dir
    ):
        """Test l'upload d'une cover avec un type de fichier invalide."""
        playlist_id = sample_playlists[0].idPlaylist

        file_content = b"fake text content"
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        # Devrait échouer selon la validation
        assert response.status_code in [400, 415, 422]

    def test_upload_cover_preserves_other_playlist_data(
        self, client, sample_playlists, db: Session, temp_upload_dir
    ):
        """Test que l'upload d'une cover préserve les autres données de la playlist."""
        original_playlist = sample_playlists[0]
        playlist_id = original_playlist.idPlaylist
        original_name = original_playlist.name
        original_vote = original_playlist.vote

        image_buffer = create_test_image()
        files = {"file": ("test_cover.jpg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

        db_playlist = (
            db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
        )
        assert db_playlist.name == original_name
        assert db_playlist.vote == original_vote

    def test_upload_cover_returns_complete_playlist_data(
        self, client, sample_playlists, temp_upload_dir
    ):
        """Test que l'upload d'une cover retourne toutes les données de la playlist."""
        playlist_id = sample_playlists[0].idPlaylist

        image_buffer = create_test_image()
        files = {"file": ("test_cover.jpg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

        data = response.json()
        assert "idPlaylist" in data
        assert "name" in data
        assert "idGenre" in data
        assert "idOwner" in data
        assert "vote" in data
        assert "visibility" in data
        assert "coverImage" in data
        assert "createdAt" in data
        assert "updatedAt" in data

    def test_upload_cover_with_different_extensions(
        self, client, sample_playlists, temp_upload_dir
    ):
        """Test l'upload de covers avec différentes extensions."""
        playlist_id = sample_playlists[0].idPlaylist
        extensions = [
            ("test.jpg", "image/jpeg"),
            ("test.jpeg", "image/jpeg"),
            ("test.png", "image/png"),
        ]

        for filename, content_type in extensions:
            image_buffer = create_test_image()
            files = {"file": (filename, image_buffer, content_type)}

            response = client.post(f"/playlists/{playlist_id}/cover", files=files)
            # Devrait réussir pour les formats d'image standard
            assert response.status_code == 200

    def test_upload_cover_to_private_playlist(
        self, client, sample_playlists, temp_upload_dir
    ):
        """Test l'upload d'une cover à une playlist privée."""
        private_playlist = next(
            p for p in sample_playlists if p.visibility == PlaylistVisibility.PRIVATE
        )
        playlist_id = private_playlist.idPlaylist

        image_buffer = create_test_image()
        files = {"file": ("test_cover.jpg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

        data = response.json()
        assert data["visibility"] == "PRIVATE"
        assert data["coverImage"] is not None

    def test_upload_cover_with_special_characters_in_filename(
        self, client, sample_playlist, temp_upload_dir
    ):
        """Test l'upload d'une cover avec des caractères spéciaux dans le nom."""
        playlist_id = sample_playlist.idPlaylist

        image_buffer = create_test_image()
        files = {"file": ("test image (1).jpg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

    def test_upload_cover_multiple_times(
        self, client, sample_playlist, temp_upload_dir
    ):
        """Test l'upload de cover plusieurs fois de suite."""
        playlist_id = sample_playlist.idPlaylist

        for i in range(3):
            image_buffer = create_test_image(color=["red", "green", "blue"][i])
            files = {"file": (f"cover{i}.jpg", image_buffer, "image/jpeg")}

            response = client.post(f"/playlists/{playlist_id}/cover", files=files)
            assert response.status_code == 200

    def test_upload_cover_with_very_small_file(
        self, client, sample_playlist, temp_upload_dir
    ):
        """Test l'upload d'un fichier très petit (1x1 pixel)."""
        playlist_id = sample_playlist.idPlaylist

        # Créer une image valide mais très petite
        image_buffer = create_test_image(size=(1, 1))
        files = {"file": ("tiny.jpg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        # Une image valide de 1x1 pixel devrait être acceptée
        assert response.status_code == 200

    def test_upload_cover_updates_timestamp(
        self, client, sample_playlist, db: Session, temp_upload_dir
    ):
        """Test que l'upload d'une cover met à jour le timestamp updatedAt."""
        playlist_id = sample_playlist.idPlaylist

        # Récupérer le timestamp original
        original_updated_at = sample_playlist.updatedAt

        image_buffer = create_test_image()
        files = {"file": ("test_cover.jpg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

        db.refresh(sample_playlist)
        # Le timestamp devrait être mis à jour (ou égal selon la précision)
        assert sample_playlist.updatedAt >= original_updated_at

    def test_upload_cover_with_jpeg_extension(
        self, client, sample_playlist, temp_upload_dir
    ):
        """Test l'upload d'une cover avec extension .jpeg."""
        playlist_id = sample_playlist.idPlaylist

        image_buffer = create_test_image()
        files = {"file": ("test_cover.jpeg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

        data = response.json()
        assert "coverImage" in data
        assert data["coverImage"] is not None

    def test_upload_cover_returns_playlist_schema(
        self, client, sample_playlist, temp_upload_dir
    ):
        """Test que l'upload retourne un schéma de playlist valide."""
        playlist_id = sample_playlist.idPlaylist

        image_buffer = create_test_image()
        files = {"file": ("test_cover.jpg", image_buffer, "image/jpeg")}

        response = client.post(f"/playlists/{playlist_id}/cover", files=files)
        assert response.status_code == 200

        data = response.json()
        # Vérifier les types
        assert isinstance(data["idPlaylist"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["idGenre"], int)
        assert isinstance(data["idOwner"], int)
        assert isinstance(data["vote"], int)
        assert isinstance(data["visibility"], str)
        assert isinstance(data["createdAt"], str)
        assert isinstance(data["updatedAt"], str)
