from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime, timedelta
import bcrypt
import jwt
import os
from typing import Optional

from repositories.user_repository import UserRepository
from models.user import User


class AuthController:
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    TOKEN_EXPIRE_HOURS = 1

    @staticmethod
    def validate_university_email(email: str) -> bool:
        """Validate that email is from University of Montpellier."""
        allowed_domains = ["@etu.umontpellier.fr", "@umontpellier.fr"]
        return any(email.endswith(domain) for domain in allowed_domains)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with automatic salt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hashed password."""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def create_jwt_token(user_id: int, role: str) -> str:
        """Create JWT token with user_id and role."""
        expiration = datetime.utcnow() + timedelta(
            hours=AuthController.TOKEN_EXPIRE_HOURS
        )
        payload = {"user_id": user_id, "role": role, "exp": expiration}
        token = jwt.encode(
            payload, AuthController.JWT_SECRET, algorithm=AuthController.JWT_ALGORITHM
        )
        return token

    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        """Decode and validate JWT token."""
        try:
            payload = jwt.decode(
                token,
                AuthController.JWT_SECRET,
                algorithms=[AuthController.JWT_ALGORITHM],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def signup(db: Session, email: str, password: str, username: str) -> dict:
        """Register a new user."""
        # Validate email domain
        if not AuthController.validate_university_email(email):
            raise HTTPException(
                status_code=400,
                detail="Email must be from @etu.umontpellier.fr or @umontpellier.fr",
            )

        # Check if user already exists
        existing_user = UserRepository.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password
        hashed_password = AuthController.hash_password(password)

        # Create user
        user = UserRepository.create_user(db, email, hashed_password, username)

        # Generate token
        token = AuthController.create_jwt_token(user.idUser, user.role.value)

        return {
            "token": token,
            "user": {
                "idUser": user.idUser,
                "email": user.email,
                "username": user.username,
                "role": user.role.value,
                "banned": user.banned,
            },
        }

    @staticmethod
    def login(db: Session, email: str, password: str) -> dict:
        """Authenticate user and return token."""
        # Get user by email
        user = UserRepository.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not AuthController.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Check if user is banned
        if user.banned:
            raise HTTPException(status_code=403, detail="Account has been banned")

        # Generate token
        token = AuthController.create_jwt_token(user.idUser, user.role.value)

        return {
            "token": token,
            "user": {
                "idUser": user.idUser,
                "email": user.email,
                "username": user.username,
                "role": user.role.value,
                "banned": user.banned,
            },
        }

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Get current user from JWT token."""
        # Decode token
        payload = AuthController.decode_jwt_token(token)
        if payload is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )

        # Get user by ID
        user = UserRepository.get_user_by_id(db, payload["user_id"])
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        # Check if user is banned
        if user.banned:
            raise HTTPException(status_code=403, detail="Account has been banned")

        return user
