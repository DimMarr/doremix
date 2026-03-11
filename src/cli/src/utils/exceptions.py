class AuthError(Exception):
    """Base exception for authentication-related errors."""


class NotAuthenticatedError(AuthError):
    """Raised when no valid authentication data is available."""


class InvalidCredentialsError(AuthError):
    """Raised when login credentials are invalid."""


class UserExistsError(AuthError):
    """Raised when trying to register an already existing user."""


class InvalidRequestError(AuthError):
    """Raised when the API rejects a malformed request."""


class TokenRefreshError(AuthError):
    """Raised when token refresh fails."""


class ApiRequestError(AuthError):
    """Raised for unexpected API/network errors."""


class ForbiddenError(AuthError):
    """Raised when the user lacks sufficient privileges (e.g : not an Admin)."""


class GenreError(Exception):
    """Base exception for genre-related errors."""


class GenreExistsError(GenreError):
    """Raised when trying to create or update a genre that already exists."""


class GenreNotFoundError(GenreError):
    """Raised when a specific genre is not found in the database."""
