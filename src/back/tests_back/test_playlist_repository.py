import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import PlaylistRepository, UserRepository
from models import Playlist, User, Genre
from models.enums import PlaylistVisibility


class TestPlaylistRepository:
    """Tests for PlaylistRepository data access methods"""

    @pytest.mark.asyncio
    async def test_get_accessible_playlists_includes_owned(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test that accessible playlists include user's own playlists"""
        playlist = Playlist(
            name="My Owned Playlist",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PRIVATE,
        )
        db.add(playlist)
        await db.commit()

        result = await PlaylistRepository.get_accessible_playlists(
            db, sample_user.idUser
        )

        assert any(p.idPlaylist == playlist.idPlaylist for p in result)

    @pytest.mark.asyncio
    async def test_get_accessible_playlists_includes_public(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test that accessible playlists include all public playlists"""
        other_user = await UserRepository.create_user(
            db=db,
            email="other@etu.umontpellier.fr",
            username="other",
            password_hash="hash",
            is_verified=True,
        )

        public_playlist = Playlist(
            name="Public Playlist",
            idOwner=other_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PUBLIC,
        )
        db.add(public_playlist)
        await db.commit()

        result = await PlaylistRepository.get_accessible_playlists(
            db, sample_user.idUser
        )

        assert any(p.idPlaylist == public_playlist.idPlaylist for p in result)

    @pytest.mark.asyncio
    async def test_get_accessible_playlists_excludes_private_other_users(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test that private playlists of other users are not included"""
        other_user = await UserRepository.create_user(
            db=db,
            email="private@etu.umontpellier.fr",
            username="private",
            password_hash="hash",
            is_verified=True,
        )

        private_playlist = Playlist(
            name="Private Playlist",
            idOwner=other_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PRIVATE,
        )
        db.add(private_playlist)
        await db.commit()

        result = await PlaylistRepository.get_accessible_playlists(
            db, sample_user.idUser
        )

        assert not any(p.idPlaylist == private_playlist.idPlaylist for p in result)

    @pytest.mark.asyncio
    async def test_get_public_playlists_returns_only_public(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test that get_public_playlists returns only PUBLIC visibility"""
        other_user = await UserRepository.create_user(
            db=db,
            email="other@etu.umontpellier.fr",
            username="other",
            password_hash="hash",
            is_verified=True,
        )

        public = Playlist(
            name="Public 1",
            idOwner=other_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PUBLIC,
        )
        private = Playlist(
            name="Private 1",
            idOwner=other_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PRIVATE,
        )
        db.add_all([public, private])
        await db.commit()

        result = await PlaylistRepository.get_public_playlists(db, sample_user)

        assert any(p.visibility == PlaylistVisibility.PUBLIC for p in result)
        for p in result:
            assert p.visibility == PlaylistVisibility.PUBLIC

    @pytest.mark.asyncio
    async def test_get_by_id_has_all_relationships(
        self, db: AsyncSession, sample_user, sample_playlist
    ):
        """Test that get_by_id includes all relationships (user, genre, tracks)"""
        result = await PlaylistRepository.get_by_id(
            db, sample_playlist.idPlaylist, sample_user
        )

        assert result is not None
        assert result.idPlaylist == sample_playlist.idPlaylist
        assert result.idOwner == sample_playlist.idOwner
        # Check relationships are loaded
        assert result.genre is not None

    @pytest.mark.asyncio
    async def test_get_by_id_nonexistent_raises_none(
        self, db: AsyncSession, sample_user
    ):
        """Test that get_by_id returns None for non-existent playlist (permission denied)"""
        result = await PlaylistRepository.get_by_id(db, 99999, sample_user)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_id_raw_returns_none_for_nonexistent(self, db: AsyncSession):
        """Test that get_by_id_raw returns None for non-existent playlist"""
        result = await PlaylistRepository.get_by_id_raw(db, 99999)
        assert result is None

    @pytest.mark.asyncio
    async def test_create_playlist_success(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test successful playlist creation"""
        new_playlist = Playlist(
            name="New Playlist",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PUBLIC,
        )

        result = await PlaylistRepository.create(db, new_playlist)

        assert result.idPlaylist is not None
        assert result.name == "New Playlist"
        assert result.idOwner == sample_user.idUser

    @pytest.mark.asyncio
    async def test_create_playlist_persists(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test that created playlist is persisted to database"""
        new_playlist = Playlist(
            name="Persist Test",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PRIVATE,
        )

        created = await PlaylistRepository.create(db, new_playlist)

        fetched = await PlaylistRepository.get_by_id_raw(db, created.idPlaylist)
        assert fetched is not None
        assert fetched.name == "Persist Test"

    @pytest.mark.asyncio
    async def test_create_playlist_vote_defaults_to_zero(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test that new playlist vote count starts at 0"""
        new_playlist = Playlist(
            name="Vote Test",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
        )

        result = await PlaylistRepository.create(db, new_playlist)
        assert result.vote == 0

    @pytest.mark.asyncio
    async def test_update_playlist_success(self, db: AsyncSession, sample_playlist):
        """Test successful playlist update"""
        sample_playlist.name = "Updated Name"
        sample_playlist.vote = 5

        result = await PlaylistRepository.update(db, sample_playlist)

        assert result.name == "Updated Name"
        assert result.vote == 5

    @pytest.mark.asyncio
    async def test_update_playlist_persists(
        self, db: AsyncSession, sample_playlist: Playlist
    ):
        """Test that updated playlist changes are persisted"""
        original_id = sample_playlist.idPlaylist
        sample_playlist.name = "New Updated Name"

        await PlaylistRepository.update(db, sample_playlist)

        fetched = await PlaylistRepository.get_by_id_raw(db, original_id)
        assert fetched is not None
        assert fetched.name == "New Updated Name"

    @pytest.mark.asyncio
    async def test_remove_nonexistent_track_returns_false(
        self, db: AsyncSession, sample_playlist
    ):
        """Test that removing non-existent track from playlist returns False"""
        result = await PlaylistRepository.remove_track(
            db, sample_playlist.idPlaylist, 99999
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_get_playlist_tracks_returns_empty_for_new_playlist(
        self, db: AsyncSession, sample_playlist
    ):
        """Test that new playlist has no tracks"""
        result = await PlaylistRepository.get_playlist_tracks(
            db, sample_playlist.idPlaylist
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_search_playlists_by_name(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test search playlists by name"""
        p1 = Playlist(
            name="Rock Classics",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
        )
        p2 = Playlist(
            name="Jazz Favorites",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
        )
        db.add_all([p1, p2])
        await db.commit()

        result = await PlaylistRepository.search_playlists(
            db,
            query="Rock",
            user_id=sample_user.idUser,
            limit=10,
        )

        assert len(result) > 0
        assert any(p.name == "Rock Classics" for p in result)

    @pytest.mark.asyncio
    async def test_can_edit_owned_playlist(
        self, db: AsyncSession, sample_user, sample_playlist
    ):
        """Test that owner can edit their playlist"""
        result = await PlaylistRepository.can_edit_playlist(
            db, sample_playlist.idPlaylist, sample_user.idUser
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_playlist_success(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test successful playlist deletion"""
        playlist = Playlist(
            name="To Delete",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
        )
        db.add(playlist)
        await db.commit()
        await db.refresh(playlist)

        playlist_id = playlist.idPlaylist

        await PlaylistRepository.delete(db, playlist)

        result = await PlaylistRepository.get_by_id_raw(db, playlist_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_name_finds_playlist(
        self, db: AsyncSession, sample_user, sample_genre
    ):
        """Test getting playlist by name"""
        p = Playlist(
            name="Unique Playlist Name",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
        )
        db.add(p)
        await db.commit()

        result = await PlaylistRepository.get_by_name(db, "Unique Playlist Name")

        assert len(result) > 0
        assert any(p.name == "Unique Playlist Name" for p in result)

    @pytest.mark.asyncio
    async def test_get_by_name_nonexistent_returns_empty(self, db: AsyncSession):
        """Test that non-existent name returns empty list"""
        result = await PlaylistRepository.get_by_name(db, "NonExistent123")

        assert result == []
