import re


def is_valid_youtube_link(url: str) -> bool:
    patterns = [
        r"^https?://(www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$",
        r"^https?://youtu\.be/[A-Za-z0-9_-]{11}$",
        r"^https?://(www\.)?youtube\.com/embed/[A-Za-z0-9_-]{11}$",
    ]

    for pattern in patterns:
        if re.match(pattern, url):
            return True

    return False
