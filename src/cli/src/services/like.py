import psutil

from src.utils.http_client import make_authenticated_request
from src.services.track import PID_FILE, CURRENT_TRACK_FILE, get_track


def get_like_status(track_id: int) -> bool:
    res = make_authenticated_request("GET", f"/tracks/{track_id}/like")
    if res.status_code == 404:
        raise Exception(f"Track #{track_id} not found.")
    if res.status_code != 200:
        raise Exception(f"Unexpected error: {res.text}")
    return bool(res.json()["isLiked"])


def like_track(track_id: int) -> str:
    track = get_track(track_id)

    if get_like_status(track_id):
        raise Exception(f"'{track.title}' is already in your liked tracks.")

    res = make_authenticated_request("POST", f"/tracks/{track_id}/like")
    if res.status_code == 404:
        raise Exception(f"Track #{track_id} not found.")
    if res.status_code != 200:
        raise Exception(f"Unexpected error: {res.text}")

    return track.title


def unlike_track(track_id: int) -> str:
    track = get_track(track_id)

    if not get_like_status(track_id):
        raise Exception(f"'{track.title}' is not in your liked tracks.")

    res = make_authenticated_request("DELETE", f"/tracks/{track_id}/like")
    if res.status_code == 404:
        raise Exception(f"Track #{track_id} not found.")
    if res.status_code != 200:
        raise Exception(f"Unexpected error: {res.text}")

    return track.title


def like_current() -> str:
    if not PID_FILE.exists():
        raise Exception("No track is currently playing. Use 'track play <id>' first.")

    pid = int(PID_FILE.read_text())
    if not psutil.pid_exists(pid):
        raise Exception("No track is currently playing (player has stopped).")

    if not CURRENT_TRACK_FILE.exists():
        raise Exception("Cannot determine the currently playing track.")

    track_id = int(CURRENT_TRACK_FILE.read_text())
    return like_track(track_id)
