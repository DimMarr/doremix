from __future__ import annotations

import requests

from src.models.genre import GenresSchema
from src.utils.exceptions import (
    ApiRequestError, 
    NotAuthenticatedError,
    ForbiddenError,
    GenreExistsError,
    GenreNotFoundError
)
from src.utils.http_client import make_authenticated_request  


def _map_genre_error(response: requests.Response, context: str) -> None:
    fallback = response.text or "No details provided by backend."
    
    if response.status_code == 400:
        raise ApiRequestError(f"{context} Cannot delete genre: it is linked to existing playlists.")
    if response.status_code == 409:
        raise GenreExistsError(f"{context}: This genre already exists.")
    if response.status_code == 404:
        raise GenreNotFoundError(f"{context}: Genre not found.")
    if response.status_code == 403:
        raise ForbiddenError(f"{context}: Access denied. Admins only.")
    if response.status_code == 401:
        raise NotAuthenticatedError(f"{context}: Session expired. Please login again.")
    
    raise ApiRequestError(f"{context}: unexpected status {response.status_code} - {fallback}")


def get_all() -> list[GenresSchema]:
    response = make_authenticated_request("GET", "/genres/")
    if response.status_code != 200:
        _map_genre_error(response, "Failed to fetch genres")
    return [GenresSchema.model_validate(g) for g in response.json()]


def create(label: str) -> GenresSchema:
    response = make_authenticated_request("POST", "/admin/genres/", json={"label": label})
    if response.status_code != 201:
        _map_genre_error(response, "Failed to create genre")
    return GenresSchema.model_validate(response.json())


def update(genre_id: int, label: str) -> GenresSchema:
    response = make_authenticated_request("PUT", f"/admin/genres/{genre_id}", json={"label": label})
    if response.status_code != 200:
        _map_genre_error(response, "Failed to update genre")
    return GenresSchema.model_validate(response.json())


def delete(genre_id: int) -> None:
    response = make_authenticated_request("DELETE", f"/admin/genres/{genre_id}")
    if response.status_code not in (200, 204):
        _map_genre_error(response, "Failed to delete genre")