from utils.get_env import get_env
from models.playlist import PlaylistSchema
from models.track import TrackSchema
import requests
import json

API_BASE_URL = get_env("API_BASE_URL")


def get_all_playlists() -> list[PlaylistSchema]:
    res = requests.get(f"{API_BASE_URL}/playlists")
    if res.status_code == 404:
        raise Exception("Playlists not found")
    data = res.json()

    # Create a PlaylistSchema Object from raw JSON data
    return [PlaylistSchema(**item) for item in data]


def get_playlist(id: str) -> PlaylistSchema:
    res = requests.get(f"{API_BASE_URL}/playlists/{id}")
    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code == 422:
        raise Exception("Playlist ID should be an integer")
    data = res.json()

    # Create a PlaylistSchema Object from raw JSON data
    return PlaylistSchema(**data)


def get_playlist_tracks(id: str) -> list[TrackSchema]:
    res = requests.get(f"{API_BASE_URL}/playlists/{id}/tracks")
    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code == 422:
        raise Exception("Playlist ID should be an integer")
    data = res.json()

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
        "visibility": visibility
        # "idOwner": user_id  # TODO: À ajouter quand l'auth sera en place
    }
    res = requests.post(f"{API_BASE_URL}/playlists/", json=payload)

    if res.status_code != 200:
        raise Exception(f"Erreur lors de la création: {res.text}")

    data = res.json()
    return PlaylistSchema(**data)

def delete_playlist(identifier: str) -> dict:
    res = requests.delete(f"{API_BASE_URL}/playlists/{identifier}")

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code != 200:
        raise Exception(f"Error while deleting: {res.text}")

    # TODO: Quand l'auth sera en place, gérer l'erreur 403 :
    # if res.status_code == 403:
    #     raise Exception("You are not the owner of this playlist")

    return res.json()

def get_playlists_by_name(name: str) -> list[PlaylistSchema]:
    res = requests.get(f"{API_BASE_URL}/playlists/name/{name}")

    if res.status_code == 404:
        raise Exception("Playlist not found")

    data = res.json()
    return [PlaylistSchema(**item) for item in data]

def update_playlist(identifier: str, name: str = None, id_genre: int = None, visibility: str = None) -> PlaylistSchema:
    payload = {}
    if name is not None:
        payload["name"] = name
    if id_genre is not None:
        payload["idGenre"] = id_genre
    if visibility is not None:
        payload["visibility"] = visibility

    # TODO: Quand l'auth sera en place, ajouter le token dans les headers

    res = requests.patch(f"{API_BASE_URL}/playlists/{identifier}", json=payload)

    if res.status_code == 404:
        raise Exception("Playlist not found")
    if res.status_code != 200:
        raise Exception(f"Error while updating: {res.text}")

    # TODO: Quand l'auth sera en place, gérer l'erreur 403 :
    # if res.status_code == 403:
    #     raise Exception("You are not the owner of this playlist")

    data = res.json()
    return PlaylistSchema(**data)