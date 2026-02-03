from cli.src.utils.get_env import get_env
from cli.src.utils.stop_process import stop_process
from cli.src.models.track import TrackSchema
import requests
import yt_dlp
import subprocess
import psutil
import os
from pathlib import Path

API_BASE_URL = get_env("API_BASE_URL")

# PID of the current song playing is stored in this file
PID_FILE = Path(f"/run/user/{os.getuid()}/yt-player.pid")


def get_track(id: int) -> TrackSchema:
    res = requests.get(f"{API_BASE_URL}/tracks/{id}")
    if res.status_code == 404:
        raise Exception("Track not found")
    data = res.json()

    # Create a PlaylistSchema Object from raw JSON data
    return TrackSchema(**data)


def get_all_tracks() -> list[TrackSchema]:
    res = requests.get(f"{API_BASE_URL}/tracks")
    data = res.json()

    return [TrackSchema(**item) for item in data]


def play_track(id: int):
    # If a track is already playing, stop it.
    if PID_FILE.exists():
        pid = int(PID_FILE.read_text())
        if psutil.pid_exists(pid):
            stop_process(pid)

    # Get Youtube Audio URL (e.g. : https://rr5---sn-25glenlz.googlevideo.com/videoplayback?expire=1767307324&ei=3KNWaevjDLaDi9oP9K7GGQ&ip=46.193.64.92&id=o-AInmKMypqBJ-SjuQMDidGmiDlItgIKIxZP2TdcWY2P-E&itag=251&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&cps=649&met=1767285724%2C&mh=7c&mm=31%2C26&mn=sn-25glenlz%2Csn-h5q7knes&ms=au%2Conr&mv=m&mvi=5&pl=19&rms=au%2Cau&initcwndbps=2622500&bui=AYUSA3BPwKzgK-pgmhJTwJZmeK9uksAwitqB-RhVi_TVdNn-PiJsQct9YshZBLvWk8iMQy3u-aT9k7wd&spc=wH4QqyPrpaLaMaeLGA&vprv=1&svpuc=1&mime=audio%2Fwebm&rqh=1&gir=yes&clen=3433755&dur=213.061&lmt=1766955883819090&mt=1767285206&fvip=4&keepalive=yes&fexp=51552689%2C51565115%2C51565681%2C51580968&c=ANDROID&txp=5532534&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Crqh%2Cgir%2Cclen%2Cdur%2Clmt&sig=AJfQdSswRgIhAL3b_GhoJMVz09HRhu9TlU8lq0wVFxwXTiQzm5Nq_EOWAiEA6Z9p_HF54q8as2Xhu7O3AMPSX4iVLKPC75aGXjKvEpo%3D&lsparams=cps%2Cmet%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRgIhAKUZCUVXrR0_CgfWncbclVzWmdoEXS9-DxaOlacQNo1RAiEA4Wdy6c1iOQaSg3euXXVyqfw1IURr0vvkTB9kCSxgLC8%3D)
    class SilentLogger:
        def debug(self, msg):
            pass

        def error(self, msg):
            pass

    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "no_warnings": True,
        "logger": SilentLogger(),
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(get_track(id).youtubeLink, download=False)
            audio_url = info["url"]
    except Exception as e:
        print(e)
        return

    # Stream with VLC from a new process
    process = subprocess.Popen(
        ["vlc", "-I", "dummy", "--play-and-exit", "--no-video", audio_url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    PID_FILE.write_text(str(process.pid))


def stop_track():
    if not PID_FILE.exists():
        return "No track is running."

    pid = int(PID_FILE.read_text())
    stop_process(pid)
    PID_FILE.unlink()
    return "Track stopped."


def search_tracks(query: str) -> list[TrackSchema]:
    res = requests.get(f"{API_BASE_URL}/tracks")

    if res.status_code != 200:
        raise Exception(f"Error while fetching tracks: {res.text}")

    data = res.json()
    all_tracks = [TrackSchema(**item) for item in data]

    query_lower = query.lower()
    filtered_tracks = [
        track for track in all_tracks if query_lower in track.title.lower()
    ]

    return filtered_tracks
