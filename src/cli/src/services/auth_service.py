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
    save_user,
    save_tokens,
)

BASE_URL = get_env("API_BASE_URL") or get_env("BACKEND_URL") or "http://localhost:8000"
ACCESS_TOKEN_EXPIRES_IN_SECONDS = 15 * 60


def _build_url(path: str) -> str:
    normalized = path if path.startswith("/") else f"/{path}"
    return f"{BASE_URL.rstrip('/')}{normalized}"


def _map_auth_error(response: requests.Response, context: str) -> None:
    detail: str
    try:
        payload = response.json()
        if isinstance(payload, dict):
            detail = str(payload.get("detail", response.text))
        else:
            detail = response.text
    except ValueError:
        detail = response.text

    if response.status_code == 400:
        raise InvalidRequestError(f"{context}: {detail}")
    if response.status_code in (401, 403):
        raise InvalidCredentialsError(f"{context}: {detail}")
    if response.status_code == 422:
        raise InvalidRequestError(f"{context}: {detail}")
    if response.status_code == 409:
        raise UserExistsError(f"{context}: {detail}")
    raise ApiRequestError(
        f"{context}: unexpected status {response.status_code} - {detail}"
    )


def register(email: str, password: str) -> dict[str, Any]:
    try:
        response = requests.post(
            _build_url("/auth/register"),
            json={"email": email, "password": password},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise ApiRequestError(f"Registration failed: {exc}") from exc

    if response.status_code != 201:
        _map_auth_error(response, "Registration failed")

    payload = response.json()
    if not isinstance(payload, dict):
        raise ApiRequestError("Registration failed: invalid backend response payload.")
    return payload


def login(email: str, password: str) -> dict[str, Any]:
    try:
        response = requests.post(
            _build_url("/auth/login"),
            json={"email": email, "password": password},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise ApiRequestError(f"Login failed: {exc}") from exc

    if response.status_code != 200:
        _map_auth_error(response, "Login failed")

    data: dict[str, Any] = response.json()
    if "access_token" not in data or "refresh_token" not in data:
        raise ApiRequestError("Login failed: missing tokens in backend response.")

    save_tokens(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=ACCESS_TOKEN_EXPIRES_IN_SECONDS,
        user=data.get("user", {}),
    )
    return data


def refresh() -> str:
    refresh_token = get_refresh_token()
    try:
        response = requests.post(
            _build_url("/auth/refresh"),
            cookies={"refresh_token": refresh_token},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise TokenRefreshError(f"Token refresh failed: {exc}") from exc

    if response.status_code != 200:
        if response.status_code == 401:
            clear_tokens()
        _map_auth_error(response, "Token refresh failed")

    data: dict[str, Any] = response.json()
    if "access_token" not in data:
        raise TokenRefreshError("Token refresh failed: missing access token.")

    user_payload = data.get("user")
    user: dict[str, Any]
    if isinstance(user_payload, dict):
        user = user_payload
    else:
        try:
            from src.utils.token_storage import get_user

            user = get_user()
        except NotAuthenticatedError:
            user = {}

    save_tokens(
        access_token=data["access_token"],
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRES_IN_SECONDS,
        user=user,
    )
    return str(data["access_token"])


def logout() -> None:
    access_token = get_access_token(allow_expired=True)
    refresh_token = get_refresh_token()

    try:
        response = requests.post(
            _build_url("/auth/logout"),
            cookies={"access_token": access_token, "refresh_token": refresh_token},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise ApiRequestError(f"Logout failed: {exc}") from exc

    if response.status_code == 401:
        refreshed_access_token = refresh()
        try:
            response = requests.post(
                _build_url("/auth/logout"),
                cookies={
                    "access_token": refreshed_access_token,
                    "refresh_token": refresh_token,
                },
                timeout=10,
            )
        except requests.RequestException as exc:
            raise ApiRequestError(f"Logout failed: {exc}") from exc

    if response.status_code not in (200, 204):
        _map_auth_error(response, "Logout failed")

    clear_tokens()


def whoami() -> dict[str, Any]:
    refresh_token = get_refresh_token()
    access_token = get_access_token(allow_expired=True)

    try:
        response = requests.get(
            _build_url("/auth/me"),
            cookies={"access_token": access_token, "refresh_token": refresh_token},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise ApiRequestError(f"Fetching current user failed: {exc}") from exc

    if response.status_code == 401:
        refreshed_access_token = refresh()
        try:
            response = requests.get(
                _build_url("/auth/me"),
                cookies={
                    "access_token": refreshed_access_token,
                    "refresh_token": refresh_token,
                },
                timeout=10,
            )
        except requests.RequestException as exc:
            raise ApiRequestError(f"Fetching current user failed: {exc}") from exc

    if response.status_code != 200:
        _map_auth_error(response, "Fetching current user failed")

    payload: dict[str, Any] = response.json()
    save_user(payload)
    return payload
