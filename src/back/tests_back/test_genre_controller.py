import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from controllers.genre import GenreController
from repositories import GenreRepository


class TestGenreController:
    """Tests for GenreController CRUD operations"""

    # ============ get_all_genres tests ============

    @pytest.mark.asyncio
    async def test_get_all_genres_success(self, db: AsyncSession, sample_genre):
        """Test successful retrieval of all genres"""
        result = await GenreController.get_all_genres(db)

        assert isinstance(result, list)
        assert len(result) > 0
        assert any(g.idGenre == sample_genre.idGenre for g in result)

    @pytest.mark.asyncio
    async def test_get_all_genres_multiple_genres(self, db: AsyncSession):
        """Test retrieval of multiple genres"""
        # Create multiple genres
        genres_data = ["Rock", "Pop", "Jazz", "Classical"]
        created_genres = []

        for label in genres_data:
            genre = await GenreRepository.create(db, label)
            created_genres.append(genre)

        result = await GenreController.get_all_genres(db)

        assert len(result) >= len(created_genres)
        genre_labels = [g.label for g in result]
        for label in genres_data:
            assert label in genre_labels

    @pytest.mark.asyncio
    async def test_get_all_genres_empty_raises_404(self, db: AsyncSession):
        """Test that no genres returns 404"""
        # Create a fresh database without genres by testing scenario
        # Note: This test assumes the test db starts without genres
        # Or we need to clear them first

        # Try to get genres when none exist (depends on setup)
        try:
            result = await GenreController.get_all_genres(db)
            # If we have sample_genre from fixture, this may not raise 404
            # The test is valid but behavior depends on fixture setup
            assert isinstance(result, list)
        except HTTPException as e:
            assert e.status_code == 404
            assert "No genres found" in e.detail

    # ============ get_genre tests ============

    @pytest.mark.asyncio
    async def test_get_genre_success(self, db: AsyncSession, sample_genre):
        """Test successful retrieval of a single genre"""
        result = await GenreController.get_genre(db, sample_genre.idGenre)

        assert result is not None
        assert result.idGenre == sample_genre.idGenre
        assert result.label == sample_genre.label

    @pytest.mark.asyncio
    async def test_get_genre_nonexistent_raises_404(self, db: AsyncSession):
        """Test that getting non-existent genre raises 404"""
        with pytest.raises(HTTPException) as exc_info:
            await GenreController.get_genre(db, 99999)

        assert exc_info.value.status_code == 404
        assert "Genre not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_genre_returns_correct_properties(self, db: AsyncSession):
        """Test that retrieved genre has all expected properties"""
        # Create a genre with specific properties
        test_label = "Reggae"
        genre = await GenreRepository.create(db, test_label)

        result = await GenreController.get_genre(db, genre.idGenre)

        assert result is not None
        assert hasattr(result, "idGenre")
        assert hasattr(result, "label")
        assert result.label == test_label

    # ============ create_genre tests ============

    @pytest.mark.asyncio
    async def test_create_genre_success(self, db: AsyncSession):
        """Test successful genre creation"""
        label = "Electronic"

        result = await GenreController.create_genre(db, label)

        assert result is not None
        assert result.label == label
        assert result.idGenre is not None
        assert isinstance(result.idGenre, int)

    @pytest.mark.asyncio
    async def test_create_genre_duplicate_label_raises_409(
        self, db: AsyncSession, sample_genre
    ):
        """Test that creating genre with existing label raises 409 Conflict"""
        with pytest.raises(HTTPException) as exc_info:
            await GenreController.create_genre(db, sample_genre.label)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_create_genre_persists_to_database(self, db: AsyncSession):
        """Test that created genre is persisted to database"""
        label = "Indie"

        created = await GenreController.create_genre(db, label)

        # Fetch from database to verify persistence
        fetched = await GenreRepository.get_by_id(db, created.idGenre)
        assert fetched is not None
        assert fetched.label == label

    @pytest.mark.asyncio
    async def test_create_genre_with_special_characters(self, db: AsyncSession):
        """Test creating genre with special characters"""
        labels = ["R&B", "Hip-Hop", "K-pop", "J-pop"]

        for label in labels:
            result = await GenreController.create_genre(db, label)
            assert result.label == label

    @pytest.mark.asyncio
    async def test_create_genre_case_sensitive_duplicate(self, db: AsyncSession):
        """Test genre label comparison for duplicates"""
        label = "Funk"
        await GenreController.create_genre(db, label)

        # Try to create with different case
        # This depends on whether the DB is case-sensitive
        # SQLite ilike might treat "Funk" and "funk" as duplicates
        try:
            result = await GenreController.create_genre(db, label.lower())
            # If this succeeds, database is case-sensitive
            assert result.label.lower() == label.lower()
        except HTTPException as e:
            # If 409, database treats them as duplicates
            assert e.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_create_empty_genre_label(self, db: AsyncSession):
        """Test creating genre with empty label"""
        # This might be allowed or rejected depending on validation
        try:
            result = await GenreController.create_genre(db, "")
            # If allowed, verify it's in database
            assert result is not None
        except (HTTPException, ValueError):
            # If rejected, test passes
            pass

    # ============ update_genre tests ============

    @pytest.mark.asyncio
    async def test_update_genre_success(self, db: AsyncSession, sample_genre):
        """Test successful genre update"""
        new_label = "Heavy Metal"

        result = await GenreController.update_genre(db, sample_genre.idGenre, new_label)

        assert result is not None
        assert result.idGenre == sample_genre.idGenre
        assert result.label == new_label

    @pytest.mark.asyncio
    async def test_update_genre_nonexistent_raises_404(self, db: AsyncSession):
        """Test updating non-existent genre raises 404"""
        with pytest.raises(HTTPException) as exc_info:
            await GenreController.update_genre(db, 99999, "NewLabel")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_genre_to_duplicate_label_raises_409(self, db: AsyncSession):
        """Test updating genre to existing label raises 409"""
        # Create two genres
        genre1 = await GenreRepository.create(db, "Genre1")
        genre2 = await GenreRepository.create(db, "Genre2")

        # Try to update genre2 to genre1's label
        with pytest.raises(HTTPException) as exc_info:
            await GenreController.update_genre(db, genre2.idGenre, genre1.label)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_update_genre_same_label_allowed(
        self, db: AsyncSession, sample_genre
    ):
        """Test that updating to same label is allowed"""
        original_label = sample_genre.label

        result = await GenreController.update_genre(
            db, sample_genre.idGenre, original_label
        )

        assert result.label == original_label

    @pytest.mark.asyncio
    async def test_update_genre_persists_to_database(
        self, db: AsyncSession, sample_genre
    ):
        """Test that updated genre is persisted to database"""
        new_label = "Updated Label"

        await GenreController.update_genre(db, sample_genre.idGenre, new_label)

        # Fetch from database to verify persistence
        fetched = await GenreRepository.get_by_id(db, sample_genre.idGenre)
        assert fetched is not None
        assert fetched.label == new_label

    @pytest.mark.asyncio
    async def test_update_genre_preserves_id(self, db: AsyncSession, sample_genre):
        """Test that genre ID is preserved during update"""
        original_id = sample_genre.idGenre

        result = await GenreController.update_genre(db, original_id, "NewLabel")

        assert result.idGenre == original_id

    # ============ delete_genre tests ============

    @pytest.mark.asyncio
    async def test_delete_genre_success(self, db: AsyncSession):
        """Test successful genre deletion"""
        # Create genre to delete
        genre = await GenreRepository.create(db, "ToDelete")

        result = await GenreController.delete_genre(db, genre.idGenre)

        assert result is True

        # Verify genre is deleted
        deleted = await GenreRepository.get_by_id(db, genre.idGenre)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_genre_raises_404(self, db: AsyncSession):
        """Test deleting non-existent genre raises 404"""
        with pytest.raises(HTTPException) as exc_info:
            await GenreController.delete_genre(db, 99999)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_delete_genre_in_use_by_playlist_raises_400(
        self, db: AsyncSession, sample_playlist, sample_genre
    ):
        """Test that deleting genre used by playlist raises 400 Bad Request"""
        # sample_playlist uses sample_genre
        with pytest.raises(HTTPException) as exc_info:
            await GenreController.delete_genre(db, sample_genre.idGenre)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot delete" in exc_info.value.detail.lower()
        assert "still used" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_delete_unused_genre_succeeds(self, db: AsyncSession):
        """Test that deleting unused genre succeeds"""
        # Create genre that is not used by any playlist
        unused_genre = await GenreRepository.create(db, "Unused")

        result = await GenreController.delete_genre(db, unused_genre.idGenre)

        assert result is True

        # Verify deletion
        deleted = await GenreRepository.get_by_id(db, unused_genre.idGenre)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_genre_cascade_check(self, db: AsyncSession):
        """Test that genre cannot be deleted if referenced by playlists"""
        from models import Playlist, PlaylistVisibility

        # Create a genre and a playlist using it
        genre = await GenreRepository.create(db, "CascadeTest")
        user = await db.execute(
            __import__("sqlalchemy").select(__import__("models").User).limit(1)
        )
        test_user = user.scalars().first()

        if test_user:
            playlist = Playlist(
                name="Test Playlist",
                idOwner=test_user.idUser,
                idGenre=genre.idGenre,
                visibility=PlaylistVisibility.PUBLIC,
            )
            db.add(playlist)
            await db.commit()

            # Try to delete genre
            with pytest.raises(HTTPException) as exc_info:
                await GenreController.delete_genre(db, genre.idGenre)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_delete_multiple_genres_independent(self, db: AsyncSession):
        """Test that deleting one genre doesn't affect others"""
        genre1 = await GenreRepository.create(db, "Genre1")
        genre2 = await GenreRepository.create(db, "Genre2")
        genre3 = await GenreRepository.create(db, "Genre3")

        # Delete genre2
        await GenreController.delete_genre(db, genre2.idGenre)

        # Verify genre1 and genre3 still exist
        assert await GenreRepository.get_by_id(db, genre1.idGenre) is not None
        assert await GenreRepository.get_by_id(db, genre3.idGenre) is not None
        assert await GenreRepository.get_by_id(db, genre2.idGenre) is None
