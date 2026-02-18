from typing import Any, Optional, cast
from src.utils.get_env import get_env
from src.models.playlist import PlaylistSchema
from src.models.track import TrackSchema
import requests

API_BASE_URL = get_env("API_BASE_URL")


def _extract_error_message(res: requests.Response) -> str:
    try:
        payload = res.json()
    except ValueError:
        return res.text or f"HTTP {res.status_code}"

    if isinstance(payload, dict):
        for key in ("detail", "message", "error"):
            value = payload.get(key)
            if isinstance(value, str):
                return value

    return res.text or f"HTTP {res.status_code}"


def _extract_items(data: Any, resource_key: str) -> list[dict[str, Any]]:
    items: list[Any]
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        for key in (resource_key, "data", "items"):
            value = data.get(key)
            if isinstance(value, list):
                items = value
                break
        else:
            raise Exception(f"Unexpected response format for {resource_key}.")
    else:
        raise Exception(f"Unexpected response format for {resource_key}.")

    if any(not isinstance(item, dict) for item in items):
        raise Exception(f"Unexpected response format for {resource_key}.")

    return cast(list[dict[str, Any]], items)


def get_accessible_playlists() -> list[PlaylistSchema]:
    res = requests.get(f"{API_BASE_URL}/playlists")
    if res.status_code == 404:
        raise Exception("Playlists not found")
    if res.status_code != 200:
        raise Exception(
            f"Error while fetching playlists: {_extract_error_message(res)}"
        )
    data = _extract_items(res.json(), "playlists")

    # Create a PlaylistSchema Object from raw JSON data
    return [PlaylistSchema(**item) for item in data]


def get_playlist(id: str) -> PlaylistSchema:
    res = requests.get(f"{API_BASE_URL}/playlists/{id}")
    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code == 422:
        raise Exception("Playlist ID should be an integer")
    if res.status_code != 200:
        raise Exception(f"Error while fetching playlist: {_extract_error_message(res)}")
    data = res.json()
    if not isinstance(data, dict):
        raise Exception("Unexpected response format for playlist.")

    # Create a PlaylistSchema Object from raw JSON data
    return PlaylistSchema(**data)


def get_playlist_tracks(id: str) -> list[TrackSchema]:
    res = requests.get(f"{API_BASE_URL}/playlists/{id}/tracks")
    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code == 422:
        raise Exception("Playlist ID should be an integer")
    if res.status_code != 200:
        raise Exception(f"Error while fetching tracks: {_extract_error_message(res)}")
    data = _extract_items(res.json(), "tracks")

    # Create a TrackSchema Object from raw JSON data
    return [TrackSchema(**item) for item in data]


def remove_track(playlist_id: str, track_id: str):
    res = requests.delete(f"{API_BASE_URL}/playlists/{playlist_id}/track/{track_id}")
    if res.status_code == 404:
        raise Exception(res.json()["detail"])
    if res.status_code == 422:
        raise Exception("Playlist ID and Track ID should be integers")
    return "Track successfully deleted."


def create_playlist(name: str, id_genre: int, visibility: str) -> PlaylistSchema:
    # TODO: Quand l'auth sera en place, la signature deviendra :
    # def create_playlist(name: str, id_genre: int, visibility: str, user_id: int) -> PlaylistSchema:
    payload = {
        "name": name,
        "idGenre": id_genre,
        "visibility": visibility,
        # "idOwner": user_id  # TODO: À ajouter quand l'auth sera en place
    }
    res = requests.post(f"{API_BASE_URL}/playlists/", json=payload)

    if res.status_code != 200:
        raise Exception(f"Erreur lors de la création: {_extract_error_message(res)}")

    data = res.json()
    if not isinstance(data, dict):
        raise Exception("Unexpected response format for playlist creation.")
    return PlaylistSchema(**data)


def delete_playlist(identifier: str) -> dict:
    res = requests.delete(f"{API_BASE_URL}/playlists/{identifier}")

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code != 200:
        raise Exception(f"Error while deleting: {_extract_error_message(res)}")

    # TODO: Quand l'auth sera en place, gérer l'erreur 403 :
    # if res.status_code == 403:
    #     raise Exception("You are not the owner of this playlist")

    data: dict[Any, Any] = res.json()
    if not isinstance(data, dict):
        raise Exception("Unexpected response format for playlist deletion.")
    return data


def update_playlist(
    playlist_id: str,
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
        payload["visibility"] = visibility

    # TODO: Quand l'auth sera en place, ajouter le token dans les headers

    res = requests.patch(f"{API_BASE_URL}/playlists/{playlist_id}", json=payload)

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code != 200:
        raise Exception(f"Error while updating: {_extract_error_message(res)}")

    # TODO: Quand l'auth sera en place, gérer l'erreur 403 :
    # if res.status_code == 403:
    #     raise Exception("You are not the owner of this playlist")

    data = res.json()
    if not isinstance(data, dict):
        raise Exception("Unexpected response format for playlist update.")
    return PlaylistSchema(**data)


def add_track_to_playlist(
    playlist_id: str, title: str, youtube_link: str
) -> TrackSchema:
    # TODO: Quand l'auth sera en place, ajouter le token dans les headers

    body = {"title": title, "url": youtube_link}

    res = requests.post(
        f"{API_BASE_URL}/playlists/{playlist_id}/tracks/by-url",
        json=body,
    )

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code == 409:
        raise Exception("Track already exists in this playlist")
    if res.status_code == 403:
        raise Exception("Invalid YouTube URL provided")
    if res.status_code != 200:
        raise Exception(f"Error while adding track: {_extract_error_message(res)}")

    # TODO: Quand l'auth sera en place, gérer l'erreur 403 :
    # if res.status_code == 403:
    #     raise Exception("You don't have permission to edit this playlist")

    data = res.json()
    if not isinstance(data, dict):
        raise Exception("Unexpected response format for track creation.")
    return TrackSchema(**data)


def search_playlists(query: str) -> list[PlaylistSchema]:
    res = requests.get(f"{API_BASE_URL}/playlists")

    if res.status_code != 200:
        raise Exception(
            f"Error while fetching playlists: {_extract_error_message(res)}"
        )

    data = _extract_items(res.json(), "playlists")
    all_playlists = [PlaylistSchema(**item) for item in data]

    query_lower = query.lower()
    filtered_playlists = [
        playlist for playlist in all_playlists if query_lower in playlist.name.lower()
    ]

    return filtered_playlists


def search_tracks_in_playlist(playlist_id: str, query: str) -> list[TrackSchema]:
    res = requests.get(f"{API_BASE_URL}/playlists/{playlist_id}/tracks")

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code != 200:
        raise Exception(f"Error while fetching tracks: {_extract_error_message(res)}")

    data = _extract_items(res.json(), "tracks")
    all_tracks = [TrackSchema(**item) for item in data]

    query_lower = query.lower()
    filtered_tracks = [
        track for track in all_tracks if query_lower in track.title.lower()
    ]

    return filtered_tracks
