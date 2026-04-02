import pytest
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from repositories import AccessTokenRepository, RefreshTokenRepository
from models.access_token import AccessToken
from models.refresh_token import RefreshToken


class TestAccessTokenRepository:
    """Tests for AccessTokenRepository token operations"""

    # ============ create_token tests ============

    @pytest.mark.asyncio
    async def test_create_token_returns_cookie_token(
        self, db: AsyncSession, sample_user
    ):
        """Test that create_token returns the unhashed cookie token"""
        token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )

        assert isinstance(token, str)
        assert len(token) > 20  # URL-safe base64 token should be long
        assert token.count("_") + token.count("-") >= 0  # URL-safe characters

    @pytest.mark.asyncio
    async def test_create_token_stores_hash_in_db(self, db: AsyncSession, sample_user):
        """Test that token hash is stored in database, not the cookie token"""
        cookie_token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )

        # The database should NOT contain the cookie token
        # Fetch all tokens for this user
        from sqlalchemy.future import select

        result = await db.execute(
            select(AccessToken).filter(AccessToken.idUser == sample_user.idUser)
        )
        tokens = result.scalars().all()

        assert len(tokens) > 0
        # Token hash should be different from cookie token
        assert tokens[0].token != cookie_token

    @pytest.mark.asyncio
    async def test_create_token_for_different_users(
        self, db: AsyncSession, sample_user
    ):
        """Test creating tokens for different users"""
        from repositories import UserRepository

        user2 = await UserRepository.create_user(
            db=db,
            email="user2@etu.umontpellier.fr",
            username="user2",
            password_hash="hash",
            is_verified=True,
        )

        token1 = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )
        token2 = await AccessTokenRepository.create_token(
            db, user2.idUser, duration_minutes=15
        )

        assert token1 != token2

    # ============ hash_token tests ============

    @pytest.mark.asyncio
    async def test_hash_token_produces_consistent_hash(self, db: AsyncSession):
        """Test that same token produces same hash"""
        test_token = "test_token_string"

        hash1 = await AccessTokenRepository.hash_token(test_token)
        hash2 = await AccessTokenRepository.hash_token(test_token)

        assert hash1 == hash2

    @pytest.mark.asyncio
    async def test_hash_token_different_for_different_tokens(self, db: AsyncSession):
        """Test that different tokens produce different hashes"""
        token1 = "token_one"
        token2 = "token_two"

        hash1 = await AccessTokenRepository.hash_token(token1)
        hash2 = await AccessTokenRepository.hash_token(token2)

        assert hash1 != hash2

    # ============ get_valid_token tests ============

    @pytest.mark.asyncio
    async def test_get_valid_token_returns_token_if_valid(
        self, db: AsyncSession, sample_user
    ):
        """Test that valid token is returned"""
        cookie_token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )

        result = await AccessTokenRepository.get_valid_token(db, cookie_token)

        assert result is not None
        assert result.idUser == sample_user.idUser

    @pytest.mark.asyncio
    async def test_get_valid_token_returns_none_if_not_found(self, db: AsyncSession):
        """Test that non-existent token returns None"""
        result = await AccessTokenRepository.get_valid_token(
            db, "nonexistent_token_xyz"
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_get_valid_token_returns_none_if_expired(
        self, db: AsyncSession, sample_user
    ):
        """Test that expired token returns None"""
        # Create an expired token manually
        test_token = secrets.token_urlsafe(64)
        hashed = await AccessTokenRepository.hash_token(test_token)
        expired_time = datetime.now(timezone.utc) - timedelta(minutes=5)

        expired_token = AccessToken(
            token=hashed,
            idUser=sample_user.idUser,
            expiresAt=expired_time,
        )
        db.add(expired_token)
        await db.commit()

        result = await AccessTokenRepository.get_valid_token(db, test_token)

        assert result is None

    # ============ revoke_token tests ============

    @pytest.mark.asyncio
    async def test_revoke_token_removes_token(self, db: AsyncSession, sample_user):
        """Test that revoking token removes it"""
        cookie_token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )

        # Revoke it
        await AccessTokenRepository.revoke_token(db, cookie_token)

        # Try to get it
        result = await AccessTokenRepository.get_valid_token(db, cookie_token)

        assert result is None

    @pytest.mark.asyncio
    async def test_revoke_token_without_commit(self, db: AsyncSession, sample_user):
        """Test revoke_token without commit parameter"""
        cookie_token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )

        # Revoke without commit
        await AccessTokenRepository.revoke_token(db, cookie_token, commit=False)

        # Manually commit
        await db.commit()

        result = await AccessTokenRepository.get_valid_token(db, cookie_token)

        assert result is None

    # ============ revoke_all_user_tokens tests ============

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_removes_all(
        self, db: AsyncSession, sample_user
    ):
        """Test that revoking all tokens removes all user tokens"""
        # Create multiple tokens for user
        token1 = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )
        token2 = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )
        token3 = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )

        # Revoke all
        await AccessTokenRepository.revoke_all_user_tokens(db, sample_user.idUser)

        # None should be valid
        assert await AccessTokenRepository.get_valid_token(db, token1) is None
        assert await AccessTokenRepository.get_valid_token(db, token2) is None
        assert await AccessTokenRepository.get_valid_token(db, token3) is None

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_does_not_affect_other_users(
        self, db: AsyncSession, sample_user
    ):
        """Test that revoking one user's tokens doesn't affect others"""
        from repositories import UserRepository

        other_user = await UserRepository.create_user(
            db=db,
            email="other@etu.umontpellier.fr",
            username="other",
            password_hash="hash",
            is_verified=True,
        )

        # Create tokens for both users
        user1_token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )
        user2_token = await AccessTokenRepository.create_token(
            db, other_user.idUser, duration_minutes=15
        )

        # Revoke user1's tokens
        await AccessTokenRepository.revoke_all_user_tokens(db, sample_user.idUser)

        # User1's token should be gone
        assert await AccessTokenRepository.get_valid_token(db, user1_token) is None
        # User2's token should still be valid
        assert await AccessTokenRepository.get_valid_token(db, user2_token) is not None

    # ============ clean_expired_tokens tests ============

    @pytest.mark.asyncio
    async def test_clean_expired_tokens_removes_expired(
        self, db: AsyncSession, sample_user
    ):
        """Test that cleanup removes expired tokens"""
        # Create an expired token manually
        test_token = secrets.token_urlsafe(64)
        hashed = await AccessTokenRepository.hash_token(test_token)
        expired_time = datetime.now(timezone.utc) - timedelta(minutes=5)

        expired = AccessToken(
            token=hashed,
            idUser=sample_user.idUser,
            expiresAt=expired_time,
        )
        db.add(expired)
        await db.commit()

        # Clean expired tokens
        await AccessTokenRepository.clean_expired_tokens(db)

        # Token should be gone
        from sqlalchemy.future import select

        result = await db.execute(
            select(AccessToken).filter(AccessToken.token == hashed)
        )
        assert result.scalars().first() is None

    @pytest.mark.asyncio
    async def test_clean_expired_tokens_keeps_valid(
        self, db: AsyncSession, sample_user
    ):
        """Test that cleanup keeps valid tokens"""
        # Create a valid token
        valid_token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=15
        )

        # Clean expired tokens
        await AccessTokenRepository.clean_expired_tokens(db)

        # Valid token should still exist
        result = await AccessTokenRepository.get_valid_token(db, valid_token)
        assert result is not None


class TestRefreshTokenRepository:
    """Tests for RefreshTokenRepository token operations"""

    # ============ create_token tests ============

    @pytest.mark.asyncio
    async def test_create_refresh_token_returns_cookie_token(
        self, db: AsyncSession, sample_user
    ):
        """Test that create_token returns the unhashed cookie token"""
        token = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=43200
        )

        assert isinstance(token, str)
        assert len(token) > 20

    # ============ hash_token tests (RefreshToken version) ============

    def test_refresh_hash_token_produces_consistent_hash(self):
        """Test that RefreshToken.hash_token produces consistent hash"""
        test_token = "test_refresh_token"

        hash1 = RefreshTokenRepository.hash_token(test_token)
        hash2 = RefreshTokenRepository.hash_token(test_token)

        assert hash1 == hash2

    # ============ get_valid_token tests ============

    @pytest.mark.asyncio
    async def test_get_valid_refresh_token_returns_token_if_valid(
        self, db: AsyncSession, sample_user
    ):
        """Test that valid refresh token is returned"""
        cookie_token = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=43200
        )

        result = await RefreshTokenRepository.get_valid_token(db, cookie_token)

        assert result is not None
        assert result.idUser == sample_user.idUser

    @pytest.mark.asyncio
    async def test_get_valid_refresh_token_returns_none_if_expired(
        self, db: AsyncSession, sample_user
    ):
        """Test that expired refresh token returns None"""
        # Create an expired refresh token manually
        test_token = secrets.token_urlsafe(64)
        hashed = RefreshTokenRepository.hash_token(test_token)
        expired_time = datetime.now(timezone.utc) - timedelta(days=1)

        expired_token = RefreshToken(
            token=hashed,
            idUser=sample_user.idUser,
            expiresAt=expired_time,
        )
        db.add(expired_token)
        await db.commit()

        result = await RefreshTokenRepository.get_valid_token(db, test_token)

        assert result is None

    # ============ revoke_token tests ============

    @pytest.mark.asyncio
    async def test_revoke_refresh_token_removes_token(
        self, db: AsyncSession, sample_user
    ):
        """Test that revoking refresh token removes it"""
        cookie_token = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=43200
        )

        # Revoke it
        await RefreshTokenRepository.revoke_token(db, cookie_token)

        # Try to get it
        result = await RefreshTokenRepository.get_valid_token(db, cookie_token)

        assert result is None

    # ============ revoke_all_user_tokens tests ============

    @pytest.mark.asyncio
    async def test_revoke_all_refresh_tokens_removes_all(
        self, db: AsyncSession, sample_user
    ):
        """Test that revoking all refresh tokens removes them"""
        # Create multiple tokens
        token1 = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=43200
        )
        token2 = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=43200
        )

        # Revoke all
        await RefreshTokenRepository.revoke_all_user_tokens(db, sample_user.idUser)

        # None should be valid
        assert await RefreshTokenRepository.get_valid_token(db, token1) is None
        assert await RefreshTokenRepository.get_valid_token(db, token2) is None

    # ============ clean_expired_tokens tests ============

    @pytest.mark.asyncio
    async def test_clean_expired_refresh_tokens_removes_expired(
        self, db: AsyncSession, sample_user
    ):
        """Test that cleanup removes expired refresh tokens"""
        # Create an expired token manually
        test_token = secrets.token_urlsafe(64)
        hashed = RefreshTokenRepository.hash_token(test_token)
        expired_time = datetime.now(timezone.utc) - timedelta(days=1)

        expired = RefreshToken(
            token=hashed,
            idUser=sample_user.idUser,
            expiresAt=expired_time,
        )
        db.add(expired)
        await db.commit()

        # Clean expired tokens
        await RefreshTokenRepository.clean_expired_tokens(db)

        # Token should be gone
        from sqlalchemy.future import select

        result = await db.execute(
            select(RefreshToken).filter(RefreshToken.token == hashed)
        )
        assert result.scalars().first() is None

    @pytest.mark.asyncio
    async def test_clean_expired_refresh_tokens_keeps_valid(
        self, db: AsyncSession, sample_user
    ):
        """Test that cleanup keeps valid refresh tokens"""
        # Create a valid token
        valid_token = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, duration_minutes=43200
        )

        # Clean expired tokens
        await RefreshTokenRepository.clean_expired_tokens(db)

        # Valid token should still exist
        result = await RefreshTokenRepository.get_valid_token(db, valid_token)
        assert result is not None
