import os
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from controllers.register import RegisterController
from schemas.user import UserRegisterSchema
from models.user import User, UserRole


class TestRegisterController:
    """Tests for RegisterController.register method"""

    @pytest.mark.asyncio
    async def test_register_success_new_user(self, db: AsyncSession):
        """Test successful registration of a new user with unique email and derived username"""
        user_data = UserRegisterSchema(
            email="john.doe@etu.umontpellier.fr",
            password="SecurePass123!",
        )

        result = await RegisterController.register(db, user_data)

        assert result == {"message": "Account successfully created"}

        # Verify user was created in database
        created_user = await db.execute(
            __import__("sqlalchemy")
            .select(User)
            .filter(User.email == "john.doe@etu.umontpellier.fr")
        )
        user = created_user.scalars().first()
        assert user is not None
        assert user.email == "john.doe@etu.umontpellier.fr"
        assert user.username == "john.doe"
        assert user.isVerified is True
        assert user.banned is False
        assert user.role == UserRole.USER

    @pytest.mark.asyncio
    async def test_register_success_extracts_username_from_email(
        self, db: AsyncSession
    ):
        """Test that username is correctly extracted from email (part before @)"""
        user_data = UserRegisterSchema(
            email="alice.smith@etu.umontpellier.fr",
            password="SecurePass123!",
        )

        await RegisterController.register(db, user_data)

        created_user = await db.execute(
            __import__("sqlalchemy")
            .select(User)
            .filter(User.email == "alice.smith@etu.umontpellier.fr")
        )
        user = created_user.scalars().first()
        assert user.username == "alice.smith"

    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises_409(
        self, db: AsyncSession, sample_user
    ):
        """Test that registering with an existing email returns 409 Conflict"""
        user_data = UserRegisterSchema(
            email=sample_user.email,
            password="SecurePass123!",
        )

        with pytest.raises(HTTPException) as exc_info:
            await RegisterController.register(db, user_data)

        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_register_missing_pepper_key_raises_500(self, db: AsyncSession):
        """Test that missing PEPPER_KEY environment variable raises 500 error"""
        user_data = UserRegisterSchema(
            email="newuser@etu.umontpellier.fr",
            password="SecurePass123!",
        )

        # Temporarily unset PEPPER_KEY
        with patch.dict(os.environ, {"PEPPER_KEY": ""}, clear=False):
            RegisterController.pepper = None
            with pytest.raises(HTTPException) as exc_info:
                await RegisterController.register(db, user_data)

            assert exc_info.value.status_code == 500
            assert "PEPPER_KEY" in exc_info.value.detail

    def test_register_email_validation_rejects_invalid_format(self):
        """Test that invalid email format is rejected by schema validation"""
        from pydantic import ValidationError

        invalid_emails = [
            "notanemail",
            "user@example.com",
            "user@etu.umontpelier.fr",  # Misspelled domain
        ]

        for email in invalid_emails:
            with pytest.raises((ValidationError, ValueError)):
                UserRegisterSchema(email=email, password="SecurePass123!")

    def test_register_password_validation_enforces_complexity(self):
        """Test that password validation enforces complexity requirements"""
        from pydantic import ValidationError

        invalid_passwords = [
            "weak",  # Too short
            "WeakPass1",  # No special char
            "weakpass1!",  # No uppercase
            "WEAKPASS1!",  # No lowercase
            "WeakPass!",  # No digit
        ]

        for password in invalid_passwords:
            with pytest.raises((ValidationError, ValueError)):
                UserRegisterSchema(
                    email="test@etu.umontpellier.fr",
                    password=password,
                )
