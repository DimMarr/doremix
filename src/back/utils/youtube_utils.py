import yt_dlp
from typing import Optional


def get_youtube_video_duration(url: str) -> Optional[int]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return int(info.get("duration"))

    except Exception as e:
        print(f"Erreur lors de la récupération : {e}")
        return None


def get_youtube_video_author(url: str) -> Optional[str]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get("uploader")

    except Exception as e:
        print(f"Erreur lors de la récupération de l'auteur : {e}")
        return None
