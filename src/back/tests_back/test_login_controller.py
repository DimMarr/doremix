import os
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from controllers.login import LoginController
from repositories import UserRepository, AccessTokenRepository, RefreshTokenRepository
from models.user import User, UserRole
from models.access_token import AccessToken
from models.refresh_token import RefreshToken

# Test password constant
TEST_PASSWORD = "TestPassword123!"


class TestLoginController:
    """Tests for LoginController authentication methods"""

    @pytest.mark.asyncio
    async def test_login_invalid_email_raises_401(self, db: AsyncSession):
        """Test login with non-existent email returns 401 Unauthorized"""
        with pytest.raises(HTTPException) as exc_info:
            await LoginController.login(
                db,
                email="nonexistent@etu.umontpellier.fr",
                password="SecurePass123!",
            )

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_wrong_password_raises_401(self, db: AsyncSession, sample_user):
        """Test login with wrong password returns 401 Unauthorized"""
        with pytest.raises(HTTPException) as exc_info:
            await LoginController.login(
                db,
                email="sarah@etu.umontpellier.fr",
                password="WrongPassword123!",
            )

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_banned_user_raises_403(self, db: AsyncSession, sample_user):
        """Test that banned user cannot login"""
        sample_user.banned = True
        await db.commit()

        with pytest.raises(HTTPException) as exc_info:
            await LoginController.login(
                db,
                email="sarah@etu.umontpellier.fr",
                password="testpassword123!",
            )

        assert exc_info.value.status_code == 403
        assert "banned" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_login_missing_pepper_key_raises_500(
        self, db: AsyncSession, sample_user
    ):
        """Test that missing PEPPER_KEY raises 500 error"""
        with patch.dict(os.environ, {"PEPPER_KEY": ""}, clear=False):
            LoginController.pepper = None
            with pytest.raises(HTTPException) as exc_info:
                await LoginController.login(
                    db,
                    email="sarah@etu.umontpellier.fr",
                    password=TEST_PASSWORD,
                )

            assert exc_info.value.status_code == 500
            assert "PEPPER_KEY" in exc_info.value.detail

    # ============ check_access_token_validity tests ============

    @pytest.mark.asyncio
    async def test_check_access_token_validity_valid_token(
        self, db: AsyncSession, sample_user
    ):
        """Test check_access_token_validity with valid token"""
        valid_token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, 15
        )

        result = await LoginController.check_access_token_validity(db, valid_token)

        assert result["access_token"] == valid_token
        assert result["validity"] is True

    @pytest.mark.asyncio
    async def test_check_access_token_validity_invalid_token_raises_401(
        self, db: AsyncSession
    ):
        """Test check_access_token_validity with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            await LoginController.check_access_token_validity(
                db, "invalid-token-string"
            )

        assert exc_info.value.status_code == 401
        assert "Invalid or expired" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_check_access_token_validity_expired_token_raises_401(
        self, db: AsyncSession, sample_user
    ):
        """Test check_access_token_validity with expired token"""
        import hashlib
        import secrets

        cookie_token = secrets.token_urlsafe(64)
        secret_key = os.getenv("TOKEN_SECRET_KEY")
        assert secret_key is not None
        combined = cookie_token + secret_key
        hashed_token = hashlib.sha256(combined.encode("utf-8")).hexdigest()

        expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)  # Expired
        db_token = AccessToken(
            token=hashed_token, idUser=sample_user.idUser, expiresAt=expires_at
        )
        db.add(db_token)
        await db.commit()

        with pytest.raises(HTTPException) as exc_info:
            await LoginController.check_access_token_validity(db, cookie_token)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    # ============ refresh_access_token tests ============

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, db: AsyncSession, sample_user):
        """Test successful refresh token use"""
        refresh_token = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, 43200
        )

        result = await LoginController.refresh_access_token(db, refresh_token)

        assert "access_token" in result
        assert "user" in result
        assert result["user"]["id"] == sample_user.idUser

    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid_token_raises_401(
        self, db: AsyncSession
    ):
        """Test refresh with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            await LoginController.refresh_access_token(db, "invalid-token")

        assert exc_info.value.status_code == 401
        assert "Invalid or expired" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_access_token_expired_token_raises_401(
        self, db: AsyncSession, sample_user
    ):
        """Test refresh with expired token"""
        import hashlib
        import secrets

        cookie_token = secrets.token_urlsafe(64)
        secret_key = os.getenv("TOKEN_SECRET_KEY")
        assert secret_key is not None
        combined = cookie_token + secret_key
        hashed_token = hashlib.sha256(combined.encode("utf-8")).hexdigest()

        expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)  # Expired
        db_token = RefreshToken(
            token=hashed_token, idUser=sample_user.idUser, expiresAt=expires_at
        )
        db.add(db_token)
        await db.commit()

        with pytest.raises(HTTPException) as exc_info:
            await LoginController.refresh_access_token(db, cookie_token)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_access_token_user_not_found_raises_404(
        self, db: AsyncSession, sample_user
    ):
        """Test refresh when user was deleted"""
        refresh_token = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, 43200
        )

        await db.delete(sample_user)
        await db.commit()

        with pytest.raises(HTTPException) as exc_info:
            await LoginController.refresh_access_token(db, refresh_token)

        assert exc_info.value.status_code == 404
        assert "User not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_refresh_access_token_banned_user_raises_403(
        self, db: AsyncSession, sample_user
    ):
        """Test refresh when user has been banned"""
        refresh_token = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, 43200
        )

        sample_user.banned = True
        await db.commit()

        with pytest.raises(HTTPException) as exc_info:
            await LoginController.refresh_access_token(db, refresh_token)

        assert exc_info.value.status_code == 403
        assert "banned" in exc_info.value.detail.lower()

    # ============ logout tests ============

    @pytest.mark.asyncio
    async def test_logout_with_tokens(self, db: AsyncSession, sample_user):
        """Test logout with valid tokens"""
        access_token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, 15
        )
        refresh_token = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, 43200
        )

        result = await LoginController.logout(db, access_token, refresh_token)
        assert result == {"message": "Successfully logged out"}

    @pytest.mark.asyncio
    async def test_logout_with_invalid_token_still_succeeds(self, db: AsyncSession):
        """Test that logout with invalid tokens still returns success"""
        result = await LoginController.logout(
            db, "invalid-access-token", "invalid-refresh-token"
        )
        assert result == {"message": "Successfully logged out"}

    # ============ logout_all_devices tests ============

    @pytest.mark.asyncio
    async def test_logout_all_devices_revokes_all_user_tokens(
        self, db: AsyncSession, sample_user
    ):
        """Test logout_all_devices revokes all tokens for a user"""
        access_token_1 = await AccessTokenRepository.create_token(
            db, sample_user.idUser, 15
        )
        access_token_2 = await AccessTokenRepository.create_token(
            db, sample_user.idUser, 15
        )
        refresh_token_1 = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, 43200
        )
        refresh_token_2 = await RefreshTokenRepository.create_token(
            db, sample_user.idUser, 43200
        )

        assert await AccessTokenRepository.get_valid_token(db, access_token_1)
        assert await AccessTokenRepository.get_valid_token(db, access_token_2)
        assert await RefreshTokenRepository.get_valid_token(db, refresh_token_1)
        assert await RefreshTokenRepository.get_valid_token(db, refresh_token_2)

        result = await LoginController.logout_all_devices(db, sample_user.idUser)
        assert result == {"message": "Successfully logged out from all devices"}

        assert await AccessTokenRepository.get_valid_token(db, access_token_1) is None
        assert await AccessTokenRepository.get_valid_token(db, access_token_2) is None
        assert await RefreshTokenRepository.get_valid_token(db, refresh_token_1) is None
        assert await RefreshTokenRepository.get_valid_token(db, refresh_token_2) is None

    @pytest.mark.asyncio
    async def test_logout_all_devices_does_not_affect_other_users(
        self, db: AsyncSession, sample_user
    ):
        """Test that logout_all_devices only affects the specified user"""
        other_user = await UserRepository.create_user(
            db=db,
            email="other@etu.umontpellier.fr",
            username="other",
            password_hash="hash",
            is_verified=True,
        )

        sample_user_token = await AccessTokenRepository.create_token(
            db, sample_user.idUser, 15
        )
        other_user_token = await AccessTokenRepository.create_token(
            db, other_user.idUser, 15
        )

        await LoginController.logout_all_devices(db, sample_user.idUser)

        assert (
            await AccessTokenRepository.get_valid_token(db, sample_user_token) is None
        )
        assert (
            await AccessTokenRepository.get_valid_token(db, other_user_token)
            is not None
        )
