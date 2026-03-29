from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.youtube_checker import run_youtube_check

scheduler = AsyncIOScheduler()


def start_scheduler():
    scheduler.add_job(
        run_youtube_check,
        trigger="interval",
        hours=12,
        id="youtube_checker",
        replace_existing=True,
    )
    scheduler.start()
    print("[scheduler] ✅ Scheduler started - checks every 12h")
