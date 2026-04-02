from __future__ import annotations

import requests

from src.utils.exceptions import (
    ApiRequestError,
    NotAuthenticatedError,
    ForbiddenError,
)
from src.utils.http_client import make_authenticated_request


def _map_mod_error(response: requests.Response, context: str) -> None:
    if response.status_code == 401:
        raise ForbiddenError(f"{context}: Access denied. Admins only.")
    if response.status_code == 418:
        raise ForbiddenError(f"{context}: User is an admin.")
    if response.status_code == 403:
        raise NotAuthenticatedError(f"{context}: User is already a moderator.")
    if response.status_code == 404:
        raise NotAuthenticatedError(f"{context}: User does not exist.")
    raise ApiRequestError(f"{context}: Unexpected status {response.status_code}")


def add_moderator(id_user: int) -> None:
    response = make_authenticated_request("PATCH", f"/users/{id_user}/add-moderator")
    if response.status_code == 401:
        raise NotAuthenticatedError("User is already a moderator.")
    if response.status_code != 200:
        return _map_mod_error(response, "Failed to add moderator")


def demote_moderator(id_user: int) -> None:
    response = make_authenticated_request("PATCH", f"/users/{id_user}/demote-moderator")
    if response.status_code == 401:
        raise NotAuthenticatedError("User is not a moderator.")
    if response.status_code != 200:
        return _map_mod_error(response, "Failed to demote moderator")
