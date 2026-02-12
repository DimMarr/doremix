from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from src.utils.exceptions import NotAuthenticatedError

CONFIG_DIR = Path.home() / ".doremix"
CONFIG_PATH = CONFIG_DIR / "config.json"


def _read_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise NotAuthenticatedError("No authentication found. Please login first.")

    try:
        content = CONFIG_PATH.read_text(encoding="utf-8")
        return dict(json.loads(content))
    except (json.JSONDecodeError, OSError) as exc:
        raise NotAuthenticatedError(
            "Authentication configuration is corrupted. Please login again."
        ) from exc


def _write_config(payload: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.chmod(CONFIG_PATH, 0o600)


def _parse_expires_at(expires_at: str | None) -> datetime:
    if not expires_at:
        raise NotAuthenticatedError("Missing token expiration. Please login again.")
    try:
        return datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise NotAuthenticatedError(
            "Invalid token expiration format. Please login again."
        ) from exc


def save_tokens(
    access_token: str,
    refresh_token: str,
    expires_in: int,
    user: dict[str, Any] | None = None,
) -> None:
    expires_at_dt = datetime.now(UTC) + timedelta(seconds=expires_in)
    payload: dict[str, Any] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at_dt.replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "user": user or {},
    }
    _write_config(payload)


def get_access_token() -> str:
    config = _read_config()
    access_token = config.get("access_token")
    if not access_token:
        raise NotAuthenticatedError("Missing access token. Please login again.")

    expires_at = _parse_expires_at(config.get("expires_at"))
    if datetime.now(UTC) >= expires_at:
        raise NotAuthenticatedError("Access token has expired.")
    return str(access_token)


def get_refresh_token() -> str:
    config = _read_config()
    refresh_token = config.get("refresh_token")
    if not refresh_token:
        raise NotAuthenticatedError("Missing refresh token. Please login again.")
    return str(refresh_token)


def get_user() -> dict[str, Any]:
    config = _read_config()
    user = config.get("user")
    if not isinstance(user, dict) or not user:
        raise NotAuthenticatedError("No user profile found. Please login again.")
    return user


def clear_tokens() -> None:
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()


def is_authenticated() -> bool:
    try:
        _ = get_access_token()
        return True
    except NotAuthenticatedError:
        return False
