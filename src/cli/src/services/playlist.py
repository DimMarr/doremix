from __future__ import annotations

from typing import Any, Literal, Optional

from src.models.playlist import PlaylistSchema, SharedUserSchema
from src.models.track import TrackSchema
from src.services import auth_service
from src.utils.http_client import make_authenticated_request

PlaylistScope = Literal["accessible", "mine", "open", "public"]


def _detail(response: Any) -> str:
    try:
        payload = response.json()
    except ValueError:
        return str(response.text)
    if isinstance(payload, dict):
        return str(payload.get("detail", payload))
    return str(payload)


def _get_current_user_id() -> int:
    try:
        current_user = auth_service.whoami()
    except Exception as exc:
        raise Exception("Authentication required. Please login first.") from exc

    user_id = current_user.get("id")
    if isinstance(user_id, int):
        return user_id
    if isinstance(user_id, str) and user_id.isdigit():
        return int(user_id)
    raise Exception("Invalid authenticated user information.")


def _visibility_value(playlist: PlaylistSchema) -> str:
    return str(playlist.visibility.value).upper()


def _can_read_playlist(playlist: PlaylistSchema, user_id: int) -> bool:
    return playlist.idOwner == user_id or _visibility_value(playlist) in {
        "PUBLIC",
        "OPEN",
    }


def _assert_can_read_playlist(playlist: PlaylistSchema, user_id: int) -> None:
    if not _can_read_playlist(playlist, user_id):
        raise Exception("You don't have permission to access this playlist.")


def _assert_owner(playlist: PlaylistSchema, user_id: int) -> None:
    if playlist.idOwner != user_id:
        raise Exception("You don't have permission to edit this playlist.")


def _is_admin() -> bool:
    try:
        current_user = auth_service.whoami()
        role = current_user.get("role", "")
        return bool(isinstance(role, str) and role.upper() == "ADMIN")
    except Exception:
        return False


def _get_playlist_from_api(id: str) -> PlaylistSchema:
    res = make_authenticated_request("GET", f"/playlists/{id}")
    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code == 422:
        raise Exception("Playlist ID should be an integer")
    if res.status_code == 401:
        raise Exception("Authentication required. Please login first.")
    if res.status_code != 200:
        raise Exception(f"Error while fetching playlist: {_detail(res)}")
    return PlaylistSchema(**res.json())


def _get_all_playlists_from_api() -> list[PlaylistSchema]:
    res = make_authenticated_request("GET", "/playlists")
    if res.status_code == 404:
        raise Exception("Playlists not found")
    if res.status_code == 401:
        raise Exception("Authentication required. Please login first.")
    if res.status_code != 200:
        raise Exception(f"Error while fetching playlists: {_detail(res)}")
    data = res.json()
    return [PlaylistSchema(**item) for item in data]


def get_all_playlists(scope: PlaylistScope = "accessible") -> list[PlaylistSchema]:
    if scope not in {"accessible", "mine", "open", "public"}:
        raise Exception("Invalid scope. Use: accessible, mine, open, public.")

    user_id = _get_current_user_id()
    playlists = _get_all_playlists_from_api()

    if scope == "mine":
        return [playlist for playlist in playlists if playlist.idOwner == user_id]
    if scope == "open":
        return [
            playlist
            for playlist in playlists
            if playlist.idOwner != user_id and _visibility_value(playlist) == "OPEN"
        ]
    if scope == "public":
        return [
            playlist
            for playlist in playlists
            if playlist.idOwner != user_id and _visibility_value(playlist) == "PUBLIC"
        ]

    return [
        playlist
        for playlist in playlists
        if playlist.idOwner == user_id
        or _visibility_value(playlist) in {"PUBLIC", "OPEN"}
    ]


def get_playlist(id: str) -> PlaylistSchema:
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(id)
    _assert_can_read_playlist(playlist, user_id)
    return playlist


def get_playlist_tracks(id: str) -> list[TrackSchema]:
    _ = get_playlist(id)

    res = make_authenticated_request("GET", f"/playlists/{id}/tracks")
    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code == 422:
        raise Exception("Playlist ID should be an integer")
    if res.status_code == 401:
        raise Exception("Authentication required. Please login first.")
    if res.status_code != 200:
        raise Exception(f"Error while fetching tracks: {_detail(res)}")
    data = res.json()
    return [TrackSchema(**item) for item in data]


def remove_track(playlist_id: str, track_id: str):
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(playlist_id)
    _assert_owner(playlist, user_id)

    res = make_authenticated_request(
        "DELETE", f"/playlists/{playlist_id}/track/{track_id}"
    )
    if res.status_code == 404:
        raise Exception(_detail(res))
    if res.status_code == 422:
        raise Exception("Playlist ID and Track ID should be integers")
    if res.status_code == 401:
        raise Exception("Authentication required. Please login first.")
    if res.status_code != 200:
        raise Exception(f"Error while removing track: {_detail(res)}")
    return "Track successfully deleted."


def create_playlist(name: str, id_genre: int, visibility: str) -> PlaylistSchema:
    payload = {
        "name": name,
        "idGenre": id_genre,
        "visibility": visibility.upper(),
    }
    res = make_authenticated_request("POST", "/playlists/", json=payload)

    if res.status_code != 200:
        raise Exception(f"Error while creating playlist: {_detail(res)}")

    data = res.json()
    return PlaylistSchema(**data)


def delete_playlist(identifier: str) -> dict:
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(identifier)
    _assert_owner(playlist, user_id)

    res = make_authenticated_request("DELETE", f"/playlists/{identifier}")

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code != 200:
        raise Exception(f"Error while deleting: {_detail(res)}")

    data: dict[Any, Any] = res.json()
    return data


def update_playlist(
    playlist_id: str,
    name: Optional[str] = None,
    id_genre: Optional[int] = None,
    visibility: Optional[str] = None,
) -> PlaylistSchema:
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(playlist_id)
    _assert_owner(playlist, user_id)

    payload: dict[str, Any] = {}
    if name is not None:
        payload["name"] = name
    if id_genre is not None:
        payload["idGenre"] = id_genre
    if visibility is not None:
        payload["visibility"] = visibility.upper()

    res = make_authenticated_request("PATCH", f"/playlists/{playlist_id}", json=payload)

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code != 200:
        raise Exception(f"Error while updating: {_detail(res)}")

    data = res.json()
    return PlaylistSchema(**data)


def add_track_to_playlist(
    playlist_id: str, title: str, youtube_link: str
) -> TrackSchema:
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(playlist_id)
    _assert_owner(playlist, user_id)

    body = {"title": title, "url": youtube_link}

    res = make_authenticated_request(
        "POST",
        f"/playlists/{playlist_id}/tracks/by-url",
        json=body,
    )

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code == 409:
        raise Exception("Track already exists in this playlist")
    if res.status_code == 403:
        detail = _detail(res).lower()
        if "invalid youtube" in detail or "invalid" in detail:
            raise Exception("Invalid YouTube URL provided")
        raise Exception("You don't have permission to edit this playlist.")
    if res.status_code != 200:
        raise Exception(f"Error while adding track: {_detail(res)}")

    data = res.json()
    return TrackSchema(**data)


def search_playlists(query: str) -> list[PlaylistSchema]:
    all_playlists = get_all_playlists("accessible")

    query_lower = query.lower()
    return [
        playlist for playlist in all_playlists if query_lower in playlist.name.lower()
    ]


def search_tracks_in_playlist(playlist_id: str, query: str) -> list[TrackSchema]:
    all_tracks = get_playlist_tracks(playlist_id)

    query_lower = query.lower()
    return [track for track in all_tracks if query_lower in track.title.lower()]


def vote_playlist(playlist_id: str, value: int) -> dict[str, Any]:
    if value not in {-1, 0, 1}:
        raise Exception(
            "Vote value must be -1 (downvote), 0 (remove vote), or 1 (upvote)."
        )

    payload = {"value": value}
    res = make_authenticated_request(
        "PUT", f"/playlists/{playlist_id}/vote", json=payload
    )

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code == 401:
        raise Exception("Authentication required. Please login first.")
    if res.status_code != 200:
        raise Exception(f"Error while voting: {_detail(res)}")

    data: dict[str, Any] = res.json()
    return data


def share_with_group(playlist_id: str, group_id: int) -> dict[str, Any]:
    res = make_authenticated_request(
        "POST",
        f"/playlists/{playlist_id}/share/group",
        json={"group_id": group_id},
    )

    if res.status_code == 404:
        raise Exception("Group not found")
    elif res.status_code == 403:
        raise Exception("You don't have permission to share this playlist.")
    elif res.status_code == 409:
        raise Exception("This group already has access to the playlist.")
    elif res.status_code not in (200, 201):
        raise Exception(f"Failed to share playlist with group: {_detail(res)}")

    data: dict[str, Any] = res.json()
    return data


def share_with_user(
    playlist_id: str, email: str, is_editor: bool = False
) -> dict[str, Any]:
    res = make_authenticated_request(
        "POST",
        f"/playlists/{playlist_id}/share/user",
        json={"target_email": email, "is_editor": is_editor},
    )

    if res.status_code == 404:
        raise Exception("User not found")
    elif res.status_code == 403:
        raise Exception("You don't have permission to share this playlist.")
    elif res.status_code == 400:
        raise Exception(_detail(res))
    elif res.status_code not in (200, 201):
        raise Exception(f"Failed to share playlist with user: {_detail(res)}")

    data: dict[str, Any] = res.json()
    return data


def transfer_ownership(
    playlist_id: str,
    email: str,
) -> dict:
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(playlist_id)
    _assert_owner(playlist, user_id)

    payload = {
        "new_owner_email": email,
    }

    res = make_authenticated_request(
        "POST",
        f"/playlists/{playlist_id}/transfer",
        json=payload,
    )

    if res.status_code == 404:
        raise Exception("Playlist or user not found")
    if res.status_code == 403:
        raise Exception("You don't have permission to transfer this playlist")
    if res.status_code != 200:
        raise Exception(f"Error while transferring ownership: {_detail(res)}")

    res_json: dict[str, Any] = res.json()
    return res_json


def reorder_track(
    playlist_id: str, track_id: int, prev_track_id: Optional[int]
) -> dict[str, Any]:
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(playlist_id)
    _assert_owner(playlist, user_id)

    payload: dict[str, Any] = {"prev_track_id": prev_track_id}

    res = make_authenticated_request(
        "PATCH",
        f"/playlists/{playlist_id}/tracks/{track_id}/move",
        json=payload,
    )

    if res.status_code == 404:
        raise Exception("Playlist or track not found")
    if res.status_code == 401:
        raise Exception("Authentication required. Please login first.")
    if res.status_code != 200:
        raise Exception(f"Error while reordering track: {_detail(res)}")

    data: dict[str, Any] = res.json()
    return data


def get_shared_users(playlist_id: str) -> list[SharedUserSchema]:
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(playlist_id)

    if playlist.idOwner != user_id and not _is_admin():
        raise Exception(
            "You don't have permission to see shared users for this playlist."
        )

    res = make_authenticated_request("GET", f"/playlists/{playlist_id}/shared-with")
    if res.status_code == 403:
        raise Exception(
            "You don't have permission to see shared users for this playlist."
        )
    if res.status_code == 404:
        raise Exception("Playlist not found.")
    if res.status_code == 401:
        raise Exception("Authentication required. Please login first.")
    if res.status_code != 200:
        raise Exception(f"Error while fetching shared users: {_detail(res)}")

    data = res.json()
    return [SharedUserSchema(**item) for item in data]


def remove_shared_user(playlist_id: str, target_user_id: str) -> dict[str, Any]:
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(playlist_id)

    if playlist.idOwner != user_id and not _is_admin():
        raise Exception("You don't have permission to remove users from this playlist.")

    res = make_authenticated_request(
        "DELETE", f"/playlists/{playlist_id}/share/user/{target_user_id}"
    )
    if res.status_code == 403:
        raise Exception("You don't have permission to remove users from this playlist.")
    if res.status_code == 404:
        raise Exception(_detail(res))
    if res.status_code == 401:
        raise Exception("Authentication required. Please login first.")
    if res.status_code != 200:
        raise Exception(f"Error while removing user: {_detail(res)}")

    data: dict[str, Any] = res.json()
    return data


def remove_shared_group(playlist_id: str, target_group_id: str) -> dict[str, Any]:
    user_id = _get_current_user_id()
    playlist = _get_playlist_from_api(playlist_id)

    if playlist.idOwner != user_id and not _is_admin():
        raise Exception(
            "You don't have permission to remove groups from this playlist."
        )

    res = make_authenticated_request(
        "DELETE", f"/playlists/{playlist_id}/share/group/{target_group_id}"
    )
    if res.status_code == 403:
        raise Exception(
            "You don't have permission to remove groups from this playlist."
        )
    if res.status_code == 404:
        raise Exception("Group is not associated with this playlist.")
    if res.status_code == 401:
        raise Exception("Authentication required. Please login first.")
    if res.status_code != 200:
        raise Exception(f"Error while removing group: {_detail(res)}")

    data: dict[str, Any] = res.json()
    return data
