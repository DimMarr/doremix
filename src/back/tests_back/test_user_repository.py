import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import UserRepository
from models.user import User, UserRole


class TestUserRepository:
    """Tests for UserRepository data access methods"""

    # ============ create tests ============

    @pytest.mark.asyncio
    async def test_create_user_success(self, db: AsyncSession):
        """Test successful user creation"""
        user = User(
            email="new@etu.umontpellier.fr",
            username="newuser",
            password="hashedpass",
            role=UserRole.USER,
        )

        result = await UserRepository.create(db, user)

        assert result.idUser is not None
        assert result.email == "new@etu.umontpellier.fr"
        assert result.username == "newuser"

    @pytest.mark.asyncio
    async def test_create_user_with_helper_success(self, db: AsyncSession):
        """Test create_user helper method"""
        result = await UserRepository.create_user(
            db=db,
            email="helper@etu.umontpellier.fr",
            username="helper",
            password_hash="bcrypt_hash",
            is_verified=True,
        )

        assert result.idUser is not None
        assert result.email == "helper@etu.umontpellier.fr"
        assert result.isVerified is True
        assert result.banned is False

    @pytest.mark.asyncio
    async def test_create_user_persists(self, db: AsyncSession):
        """Test that created user is persisted to database"""
        created = await UserRepository.create_user(
            db=db,
            email="persist@etu.umontpellier.fr",
            username="persist",
            password_hash="hash",
            is_verified=False,
        )

        # Fetch from database
        fetched = await UserRepository.get_user_by_id(db, created.idUser)
        assert fetched is not None
        assert fetched.email == "persist@etu.umontpellier.fr"

    # ============ get_all tests ============

    @pytest.mark.asyncio
    async def test_get_all_users_returns_list(self, db: AsyncSession, sample_user):
        """Test that get_all returns all users"""
        result = await UserRepository.get_all(db)

        assert isinstance(result, list)
        assert len(result) > 0
        assert any(u.idUser == sample_user.idUser for u in result)

    @pytest.mark.asyncio
    async def test_get_all_includes_multiple_users(self, db: AsyncSession):
        """Test that get_all includes multiple users"""
        # Create multiple users
        for i in range(3):
            await UserRepository.create_user(
                db=db,
                email=f"user{i}@etu.umontpellier.fr",
                username=f"user{i}",
                password_hash="hash",
                is_verified=True,
            )

        result = await UserRepository.get_all(db)

        assert len(result) >= 3

    # ============ get_user_by_id tests ============

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, db: AsyncSession, sample_user):
        """Test retrieving user by ID"""
        result = await UserRepository.get_user_by_id(db, sample_user.idUser)

        assert result is not None
        assert result.idUser == sample_user.idUser
        assert result.email == sample_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_nonexistent_returns_none(self, db: AsyncSession):
        """Test that non-existent user ID returns None"""
        result = await UserRepository.get_user_by_id(db, 99999)

        assert result is None

    # ============ get_by_email tests ============

    @pytest.mark.asyncio
    async def test_get_by_email_success(self, db: AsyncSession, sample_user):
        """Test retrieving user by email"""
        result = await UserRepository.get_by_email(db, "sarah@etu.umontpellier.fr")

        assert result is not None
        assert result.email == "sarah@etu.umontpellier.fr"
        assert result.idUser == sample_user.idUser

    @pytest.mark.asyncio
    async def test_get_by_email_nonexistent_returns_none(self, db: AsyncSession):
        """Test that non-existent email returns None"""
        result = await UserRepository.get_by_email(
            db, "nonexistent@etu.umontpellier.fr"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_case_sensitive(self, db: AsyncSession, sample_user):
        """Test that email lookup is case-sensitive or insensitive (DB-dependent)"""
        # Try with different case
        result = await UserRepository.get_by_email(db, "SARAH@etu.umontpellier.fr")

        # Result depends on database collation
        # SQLite is typically case-insensitive, PostgreSQL is case-sensitive
        # This test documents the behavior
        if result:
            assert result.idUser == sample_user.idUser

    # ============ get_by_username tests ============

    @pytest.mark.asyncio
    async def test_get_by_username_success(self, db: AsyncSession, sample_user):
        """Test retrieving user by username"""
        result = await UserRepository.get_by_username(db, "sarah")

        assert result is not None
        assert result.username == "sarah"
        assert result.idUser == sample_user.idUser

    @pytest.mark.asyncio
    async def test_get_by_username_nonexistent_returns_none(self, db: AsyncSession):
        """Test that non-existent username returns None"""
        result = await UserRepository.get_by_username(db, "nonexistent_user")

        assert result is None

    # ============ search_users tests ============

    @pytest.mark.asyncio
    async def test_search_users_by_username(self, db: AsyncSession, sample_user):
        """Test searching users by username"""
        result = await UserRepository.search_users(db, "sarah")

        assert len(result) > 0
        assert any(u.username == "sarah" for u in result)

    @pytest.mark.asyncio
    async def test_search_users_by_email(self, db: AsyncSession, sample_user):
        """Test searching users by email"""
        result = await UserRepository.search_users(db, "sarah@etu")

        assert len(result) > 0
        assert any(u.email == "sarah@etu.umontpellier.fr" for u in result)

    @pytest.mark.asyncio
    async def test_search_users_partial_match(self, db: AsyncSession):
        """Test that search supports partial matching"""
        # Create users with searchable names
        await UserRepository.create_user(
            db=db,
            email="john@etu.umontpellier.fr",
            username="john_developer",
            password_hash="hash",
            is_verified=True,
        )
        await UserRepository.create_user(
            db=db,
            email="jane@etu.umontpellier.fr",
            username="jane_developer",
            password_hash="hash",
            is_verified=True,
        )

        result = await UserRepository.search_users(db, "developer")

        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_search_users_respects_limit(self, db: AsyncSession):
        """Test that search respects result limit"""
        # Create multiple users
        for i in range(10):
            await UserRepository.create_user(
                db=db,
                email=f"search{i}@etu.umontpellier.fr",
                username=f"search{i}",
                password_hash="hash",
                is_verified=True,
            )

        result = await UserRepository.search_users(db, "search", limit=3)

        assert len(result) <= 3

    # ============ update_role tests ============

    @pytest.mark.asyncio
    async def test_update_role_to_moderator(self, db: AsyncSession, sample_user):
        """Test updating user role to MODERATOR"""
        result = await UserRepository.update_role(
            db, sample_user.idUser, UserRole.MODERATOR
        )

        assert result is not None
        assert result.role == UserRole.MODERATOR

    @pytest.mark.asyncio
    async def test_update_role_to_admin(self, db: AsyncSession, sample_user):
        """Test updating user role to ADMIN"""
        result = await UserRepository.update_role(
            db, sample_user.idUser, UserRole.ADMIN
        )

        assert result is not None
        assert result.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_update_role_persists(self, db: AsyncSession, sample_user):
        """Test that role update is persisted to database"""
        await UserRepository.update_role(db, sample_user.idUser, UserRole.MODERATOR)

        fetched = await UserRepository.get_user_by_id(db, sample_user.idUser)
        assert fetched is not None
        assert fetched.role == UserRole.MODERATOR

    @pytest.mark.asyncio
    async def test_update_role_nonexistent_returns_none(self, db: AsyncSession):
        """Test that updating non-existent user returns None"""
        result = await UserRepository.update_role(db, 99999, UserRole.ADMIN)

        assert result is None

    @pytest.mark.asyncio
    async def test_mark_as_verified_nonexistent_returns_none(self, db: AsyncSession):
        """Test that verifying non-existent user returns None"""
        result = await UserRepository.mark_as_verified(db, 99999)

        assert result is None

    # ============ get_non_admin_ban_candidates tests ============

    @pytest.mark.asyncio
    async def test_get_non_admin_ban_candidates_excludes_admin(
        self, db: AsyncSession, sample_user
    ):
        """Test that admin users are excluded from ban candidates"""
        # Make sample_user an admin
        admin = await UserRepository.create_user(
            db=db,
            email="admin@etu.umontpellier.fr",
            username="admin",
            password_hash="hash",
            is_verified=True,
        )
        await UserRepository.update_role(db, admin.idUser, UserRole.ADMIN)

        result = await UserRepository.get_non_admin_ban_candidates(
            db, sample_user.idUser
        )

        assert not any(u.idUser == admin.idUser for u in result)

    @pytest.mark.asyncio
    async def test_get_non_admin_ban_candidates_excludes_requestor(
        self, db: AsyncSession, sample_user
    ):
        """Test that requesting user is excluded"""
        result = await UserRepository.get_non_admin_ban_candidates(
            db, sample_user.idUser
        )

        assert not any(u.idUser == sample_user.idUser for u in result)

    @pytest.mark.asyncio
    async def test_get_non_admin_ban_candidates_excludes_banned(
        self, db: AsyncSession, sample_user
    ):
        """Test that already banned users are excluded"""
        # Create and ban a user
        banned_user = await UserRepository.create_user(
            db=db,
            email="banned@etu.umontpellier.fr",
            username="banned",
            password_hash="hash",
            is_verified=True,
        )
        banned_user.banned = True
        await db.commit()

        result = await UserRepository.get_non_admin_ban_candidates(
            db, sample_user.idUser
        )

        assert not any(u.idUser == banned_user.idUser for u in result)

    @pytest.mark.asyncio
    async def test_get_non_admin_ban_candidates_includes_regular_users(
        self, db: AsyncSession, sample_user
    ):
        """Test that regular non-banned users are included"""
        # Create a regular user
        regular = await UserRepository.create_user(
            db=db,
            email="regular@etu.umontpellier.fr",
            username="regular",
            password_hash="hash",
            is_verified=True,
        )

        result = await UserRepository.get_non_admin_ban_candidates(
            db, sample_user.idUser
        )

        assert any(u.idUser == regular.idUser for u in result)

    @pytest.mark.asyncio
    async def test_get_non_admin_ban_candidates_includes_moderators(
        self, db: AsyncSession, sample_user
    ):
        """Test that moderators can be banned (only admins excluded)"""
        # Create a moderator
        mod = await UserRepository.create_user(
            db=db,
            email="mod@etu.umontpellier.fr",
            username="mod",
            password_hash="hash",
            is_verified=True,
        )
        await UserRepository.update_role(db, mod.idUser, UserRole.MODERATOR)

        result = await UserRepository.get_non_admin_ban_candidates(
            db, sample_user.idUser
        )

        assert any(u.idUser == mod.idUser for u in result)

    @pytest.mark.asyncio
    async def test_get_non_admin_ban_candidates_ordered_by_id(
        self, db: AsyncSession, sample_user
    ):
        """Test that results are ordered by user ID"""
        # Create multiple users
        users = []
        for i in range(3):
            u = await UserRepository.create_user(
                db=db,
                email=f"ordered{i}@etu.umontpellier.fr",
                username=f"ordered{i}",
                password_hash="hash",
                is_verified=True,
            )
            users.append(u)

        result = await UserRepository.get_non_admin_ban_candidates(
            db, sample_user.idUser
        )

        # Check that IDs are in ascending order
        for i in range(len(result) - 1):
            assert result[i].idUser < result[i + 1].idUser
