from utils.get_env import get_env
from models.track import TrackSchema
import requests

API_BASE_URL = get_env("API_BASE_URL")


def get_all_tracks() -> list[TrackSchema]:
    res = requests.get(f"{API_BASE_URL}/tracks")
    data = res.json()

    return [TrackSchema(**item) for item in data]


def get_track(id: int) -> TrackSchema:
    res = requests.get(f"{API_BASE_URL}/tracks/{id}")

    if res.status_code == 404:
        raise Exception("Track not found")

    data = res.json()
    return TrackSchema(**data)