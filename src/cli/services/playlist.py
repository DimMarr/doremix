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
