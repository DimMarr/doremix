import pytest
import pytest_asyncio
from unittest.mock import patch, call
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import yt_dlp

from jobs.youtube_checker import check_youtube_status, run_youtube_check
from models.track import Track, TrackStatus


class TestCheckYoutubeStatus:
    """Tests for the check_youtube_status function."""

    @patch("jobs.youtube_checker.yt_dlp.YoutubeDL")
    def test_status_ok(self, mock_youtube_dl):
        """Test that a valid, available video returns TrackStatus.ok."""
        mock_ydl_instance = mock_youtube_dl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {"availability": "public"}

        status = check_youtube_status("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert status == TrackStatus.ok
        mock_ydl_instance.extract_info.assert_called_once()

    @patch("jobs.youtube_checker.yt_dlp.YoutubeDL")
    def test_status_private_from_availability(self, mock_youtube_dl):
        """Test that a video requiring auth returns TrackStatus.unavailable."""
        mock_ydl_instance = mock_youtube_dl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {"availability": "needs_auth"}

        status = check_youtube_status("https://www.youtube.com/watch?v=private_video")
        assert status == TrackStatus.unavailable

    @patch("jobs.youtube_checker.yt_dlp.YoutubeDL")
    def test_status_private_from_exception(self, mock_youtube_dl):
        """Test that a DownloadError with 'private' returns TrackStatus.unavailable."""
        mock_ydl_instance = mock_youtube_dl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "This video is private."
        )

        status = check_youtube_status("https://www.youtube.com/watch?v=private_video")
        assert status == TrackStatus.unavailable

    @patch("jobs.youtube_checker.yt_dlp.YoutubeDL")
    def test_status_geo_blocked(self, mock_youtube_dl):
        """Test that a DownloadError with 'geographic' returns TrackStatus.unavailable."""
        mock_ydl_instance = mock_youtube_dl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "This video is not available in your country due to geographic restrictions."
        )

        status = check_youtube_status("https://www.youtube.com/watch?v=geoblocked")
        assert status == TrackStatus.unavailable

    @patch("jobs.youtube_checker.yt_dlp.YoutubeDL")
    def test_status_unavailable_from_download_error(self, mock_youtube_dl):
        """Test that a generic DownloadError returns TrackStatus.unavailable."""
        mock_ydl_instance = mock_youtube_dl.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.side_effect = yt_dlp.utils.DownloadError(
            "Video unavailable"
        )

        status = check_youtube_status(
            "https://www.youtube.com/watch?v=unavailable_video"
        )
        assert status == TrackStatus.unavailable


@pytest_asyncio.fixture
async def tracks_for_check(db: AsyncSession):
    """Creates sample tracks for the youtube checker job."""
    tracks_data = [
        {
            "title": "OK Track",
            "youtubeLink": "https://www.youtube.com/watch?v=ok_video",
            "status": TrackStatus.ok,
        },
        {
            "title": "Unavailable Track",
            "youtubeLink": "https://www.youtube.com/watch?v=unavailable_video",
            "status": TrackStatus.ok,
        },
    ]
    tracks = [Track(**data) for data in tracks_data]
    db.add_all(tracks)
    await db.commit()
    for t in tracks:
        await db.refresh(t)
    return tracks


class TestRunYoutubeCheck:
    """Tests for the run_youtube_check cron job."""

    @pytest.mark.asyncio
    @patch("jobs.youtube_checker.check_youtube_status")
    @patch("jobs.youtube_checker.AsyncSessionLocal")
    async def test_updates_track_statuses(
        self, mock_session_local, mock_check_status, db: AsyncSession, tracks_for_check
    ):
        """Test that the job correctly updates track statuses in the database."""
        mock_session_local.return_value.__aenter__.return_value = db

        def check_status_side_effect(url):
            if "ok_video" in url:
                return TrackStatus.ok
            if "unavailable_video" in url:
                return TrackStatus.unavailable
            return TrackStatus.ok

        mock_check_status.side_effect = check_status_side_effect
        await run_youtube_check()

        expected_calls = [
            call("https://www.youtube.com/watch?v=ok_video"),
            call("https://www.youtube.com/watch?v=unavailable_video"),
        ]
        assert mock_check_status.call_count == 2
        mock_check_status.assert_has_calls(expected_calls, any_order=True)

        result = await db.execute(select(Track).order_by(Track.title))
        track_map = {t.title: t for t in result.scalars().all()}

        assert track_map["Unavailable Track"].status == TrackStatus.unavailable
        assert track_map["OK Track"].status == TrackStatus.ok

    @pytest.mark.asyncio
    @patch("jobs.youtube_checker.AsyncSessionLocal")
    @patch(
        "jobs.youtube_checker.check_youtube_status",
        return_value=TrackStatus.unavailable,
    )
    async def test_rollback_on_error(
        self, mock_check_status, mock_session_local, db: AsyncSession
    ):
        """Test that changes are rolled back if an error occurs during commit."""
        track = Track(
            title="Test Rollback",
            youtubeLink="https://www.youtube.com/watch?v=test_rollback",
            status=TrackStatus.ok,
        )
        db.add(track)
        await db.commit()
        await db.refresh(track)
        track_id = track.idTrack

        mock_session_local.return_value.__aenter__.return_value = db

        with patch.object(db, "commit", side_effect=Exception("Commit failed")):
            await run_youtube_check()

        await db.rollback()
        refetched_track = await db.get(Track, track_id)
        assert refetched_track.status == TrackStatus.ok
