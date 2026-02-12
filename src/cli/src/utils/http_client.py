from __future__ import annotations

# Waiting for real backend implementation to use in Services

from typing import Any

import requests

from src.services import auth_service
from src.utils.exceptions import ApiRequestError, NotAuthenticatedError
from src.utils.get_env import get_env
from src.utils.token_storage import get_access_token

BASE_URL = get_env("API_BASE_URL") or "http://localhost:8000"


def _build_url(endpoint: str) -> str:
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    return f"{BASE_URL.rstrip('/')}{endpoint}"


def make_authenticated_request(
    method: str, endpoint: str, **kwargs: Any
) -> requests.Response:
    url = _build_url(endpoint)
    headers = dict(kwargs.pop("headers", {}))
    retried = False

    while True:
        token = get_access_token()
        headers["Authorization"] = f"Bearer {token}"

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                timeout=kwargs.pop("timeout", 10),
                **kwargs,
            )
        except requests.RequestException as exc:
            raise ApiRequestError(f"Request failed: {exc}") from exc

        if response.status_code != 401 or retried:
            return response

        try:
            auth_service.refresh()
        except NotAuthenticatedError:
            raise
        except Exception as exc:
            raise NotAuthenticatedError(
                "Authentication expired and token refresh failed. Please login again."
            ) from exc
        retried = True
