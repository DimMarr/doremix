from __future__ import annotations

from typing import Any, Optional

import requests

from src.models.playlist import PlaylistSchema
from src.models.track import TrackSchema
from src.utils.exceptions import (
    ApiRequestError,
    ForbiddenError,
    NotAuthenticatedError,
    PlaylistNotFoundError,
)
from src.utils.http_client import make_authenticated_request


def _detail(response: Any) -> str:
    try:
        payload = response.json()
    except ValueError:
        return str(response.text)
    if isinstance(payload, dict):
        return str(payload.get("detail", payload))
    return str(payload)


def _map_playlist_error(response: requests.Response, context: str) -> None:
    fallback = response.text or "No details provided by backend."
    if response.status_code == 404:
        raise PlaylistNotFoundError(f"{context}: Playlist not found.")
    if response.status_code == 403:
        raise ForbiddenError(f"{context}: Access denied. Admins only.")
    if response.status_code == 401:
        raise NotAuthenticatedError(
            f"{context}: Session expired. Please login again."
        )
    raise ApiRequestError(
        f"{context}: unexpected status {response.status_code} - {fallback}"
    )


def get_all_playlists() -> list[PlaylistSchema]:
    response = make_authenticated_request("GET", "/admin/playlists/")
    if response.status_code != 200:
        _map_playlist_error(response, "Failed to fetch playlists")
    return [PlaylistSchema.model_validate(p) for p in response.json()]


def get_playlist_tracks(playlist_id: int) -> list[TrackSchema]:
    response = make_authenticated_request(
        "GET", f"/admin/playlists/{playlist_id}/tracks"
    )
    if response.status_code != 200:
        _map_playlist_error(response, "Failed to fetch tracks")
    return [TrackSchema.model_validate(t) for t in response.json()]


def update_playlist(
    playlist_id: int,
    name: Optional[str] = None,
    id_genre: Optional[int] = None,
    visibility: Optional[str] = None,
) -> PlaylistSchema:
    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if id_genre is not None:
        payload["idGenre"] = id_genre
    if visibility is not None:
        payload["visibility"] = visibility.upper()

    response = make_authenticated_request(
        "PATCH", f"/admin/playlists/{playlist_id}", json=payload
    )
    if response.status_code != 200:
        _map_playlist_error(response, "Failed to update playlist")
    return PlaylistSchema.model_validate(response.json())


def delete_playlist(playlist_id: int) -> dict:
    response = make_authenticated_request(
        "DELETE", f"/admin/playlists/{playlist_id}"
    )
    if response.status_code not in (200, 204):
        _map_playlist_error(response, "Failed to delete playlist")
    return response.json() if response.status_code == 200 else {}


def add_track(playlist_id: int, title: str, url: str) -> TrackSchema:
    body = {"title": title, "url": url}
    response = make_authenticated_request(
        "POST", f"/admin/playlists/{playlist_id}/tracks/by-url", json=body
    )
    if response.status_code != 200:
        _map_playlist_error(response, "Failed to add track")
    return TrackSchema.model_validate(response.json())


def remove_track(playlist_id: int, track_id: int) -> PlaylistSchema:
    response = make_authenticated_request(
        "DELETE", f"/admin/playlists/{playlist_id}/track/{track_id}"
    )
    if response.status_code != 200:
        _map_playlist_error(response, "Failed to remove track")
    return PlaylistSchema.model_validate(response.json())
