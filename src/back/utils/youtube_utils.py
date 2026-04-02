import yt_dlp
from typing import Optional, Tuple, cast


def get_youtube_video_info(
    url: str,
) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = int(info.get("duration")) if info.get("duration") else None
            author = info.get("uploader")
            channel_url = info.get("uploader_url") or info.get("channel_url")
            return duration, author, channel_url

    # Signal unavailable videos with a sentinel author value.
    except yt_dlp.utils.DownloadError:
        return None, "Video unavailable", None
    except Exception as e:
        print(f"Error fetching YouTube info: {e}")
        return None, None, None


def get_youtube_channel_avatar(channel_url: str) -> Optional[str]:
    """
    Fetches the profile avatar of a YouTube channel.
    Uses the /about page to get the channel metadata (avatar).
    """
    if not channel_url:
        return None

    # Append /about to get only channel metadata, not the video list
    about_url = channel_url.rstrip("/") + "/about"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(about_url, download=False)
            thumbnails = info.get("thumbnails", [])
            # Prefer the explicit avatar thumbnail
            for thumb in thumbnails:
                thumb_id = str(thumb.get("id", "")).lower()
                if "avatar" in thumb_id:
                    return cast(Optional[str], thumb.get("url"))
            # Fallback: first thumbnail on a channel page is usually the avatar
            if thumbnails:
                return cast(Optional[str], thumbnails[0].get("url"))

    except Exception as e:
        print(f"Error fetching channel avatar for {channel_url}: {e}")
    return None


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
