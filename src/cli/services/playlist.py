from utils.get_env import get_env
from models.playlist import PlaylistSchema
from models.track import TrackSchema
import requests
import json

API_BASE_URL = get_env("API_BASE_URL")


def get_all_playlists() -> list[PlaylistSchema]:
    res = requests.get(f"{API_BASE_URL}/playlists")
    data = res.json()

    # Create a PlaylistSchema Object from raw JSON data
    return [PlaylistSchema(**item) for item in data]


def get_playlist(id: str) -> PlaylistSchema:
    res = requests.get(f"{API_BASE_URL}/playlists/{id}")
    data = res.json()

    # Create a PlaylistSchema Object from raw JSON data
    return PlaylistSchema(**data)


def get_playlist_tracks(id: str) -> list[TrackSchema]:
    res = requests.get(f"{API_BASE_URL}/playlists/{id}/tracks")
    data = res.json()

    # Create a TrackSchema Object from raw JSON data
    return [TrackSchema(**item) for item in data]
