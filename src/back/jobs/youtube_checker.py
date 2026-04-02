import yt_dlp
from sqlalchemy.future import select
from database import AsyncSessionLocal
from models.track import Track, TrackStatus


def check_youtube_status(url: str) -> TrackStatus:
    ydl_opts = {"quiet": True, "no_warnings": True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            availability = info.get("availability", "")
            if availability in ("needs_auth", "subscriber_only"):
                return TrackStatus.unavailable
            return TrackStatus.ok
    except yt_dlp.utils.DownloadError:
        return TrackStatus.unavailable
    except Exception as e:
        print(f"[youtube_checker] Error checking on {url}: {e}")
        return TrackStatus.unavailable


async def run_youtube_check():
    print("[youtube_checker] Starting scan ...")
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Track).filter(Track.youtubeLink.isnot(None))
            )
            tracks = list(result.scalars().all())
            counts = {s.value: 0 for s in TrackStatus}

            for track in tracks:
                status = check_youtube_status(track.youtubeLink)
                track.status = status
                counts[status.value] += 1

            await db.commit()
            print(f"[youtube_checker] ✅ Scan finished — {counts}")
        except Exception as e:
            await db.rollback()
            print(f"[youtube_checker] ❌ Erreur : {e}")
