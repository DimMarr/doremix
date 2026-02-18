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
