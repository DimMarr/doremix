import yt_dlp
from typing import Optional, Tuple


def get_youtube_video_info(url: str) -> Tuple[Optional[int], Optional[str]]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = int(info.get("duration")) if info.get("duration") else None
            author = info.get("uploader")
            return duration, author

    # Return an error if the video doesn't exists
    except yt_dlp.utils.DownloadError:
        return "Video unavailable", None
    except Exception as e:
        print(f"Error fetching YouTube info: {e}")
        return None, None


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
            uploader: Optional[str] = info.get("uploader")
            return uploader

    except Exception as e:
        print(f"Erreur lors de la récupération de l'auteur : {e}")
        return None
