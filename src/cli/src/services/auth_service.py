from __future__ import annotations

from typing import Any

import requests

from src.utils.exceptions import (
    ApiRequestError,
    InvalidCredentialsError,
    InvalidRequestError,
    NotAuthenticatedError,
    TokenRefreshError,
    UserExistsError,
)
from src.utils.get_env import get_env
from src.utils.token_storage import (
    clear_tokens,
    get_access_token,
    get_refresh_token,
    save_tokens,
)

BASE_URL = get_env("API_BASE_URL") or "http://localhost:8000"


def _build_url(path: str) -> str:
    return f"{BASE_URL.rstrip('/')}{path}"


def _map_auth_error(response: requests.Response, context: str) -> None:
    detail: str
    try:
        payload = response.json()
        detail = payload.get("detail", response.text)
    except ValueError:
        detail = response.text

    if response.status_code == 400:
        raise InvalidRequestError(f"{context}: {detail}")
    if response.status_code == 401:
        raise InvalidCredentialsError(f"{context}: {detail}")
    if response.status_code == 409:
        raise UserExistsError(f"{context}: {detail}")
    raise ApiRequestError(
        f"{context}: unexpected status {response.status_code} - {detail}"
    )


def register(email: str, password: str, username: str) -> dict[str, Any]:
    try:
        response = requests.post(
            _build_url("/api/auth/register"),
            json={"email": email, "password": password, "username": username},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise ApiRequestError(f"Registration failed: {exc}") from exc

    if response.status_code != 201:
        _map_auth_error(response, "Registration failed")

    data: dict[str, Any] = response.json()
    save_tokens(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=int(data["expires_in"]),
        user=data.get("user", {}),
    )
    return data


def login(email: str, password: str) -> dict[str, Any]:
    try:
        response = requests.post(
            _build_url("/api/auth/login"),
            json={"email": email, "password": password},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise ApiRequestError(f"Login failed: {exc}") from exc

    if response.status_code != 200:
        _map_auth_error(response, "Login failed")

    data: dict[str, Any] = response.json()
    save_tokens(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=int(data["expires_in"]),
        user=data.get("user", {}),
    )
    return data


def refresh() -> str:
    refresh_token = get_refresh_token()
    try:
        response = requests.post(
            _build_url("/api/auth/refresh"),
            json={"refresh_token": refresh_token},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise TokenRefreshError(f"Token refresh failed: {exc}") from exc

    if response.status_code != 200:
        if response.status_code == 401:
            clear_tokens()
        _map_auth_error(response, "Token refresh failed")

    data: dict[str, Any] = response.json()
    # Preserve existing user payload when refresh response does not include one.
    user: dict[str, Any] = {}
    try:
        from src.utils.token_storage import get_user

        user = get_user()
    except NotAuthenticatedError:
        user = {}

    save_tokens(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=int(data["expires_in"]),
        user=user,
    )
    return str(data["access_token"])


def logout() -> None:
    access_token = get_access_token()
    refresh_token = get_refresh_token()
    try:
        response = requests.post(
            _build_url("/api/auth/logout"),
            headers={"Authorization": f"Bearer {access_token}"},
            json={"refresh_token": refresh_token},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise ApiRequestError(f"Logout failed: {exc}") from exc

    if response.status_code not in (200, 204):
        _map_auth_error(response, "Logout failed")

    clear_tokens()
