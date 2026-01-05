from utils.get_env import get_env
from models.track import TrackSchema
import requests

API_BASE_URL = get_env("API_BASE_URL")

def get_track(id: int) -> TrackSchema:
    res = requests.get(f'{API_BASE_URL}/tracks/{id}')
    data = res.json()

    # Create a PlaylistSchema Object from raw JSON data
    return TrackSchema(**data)