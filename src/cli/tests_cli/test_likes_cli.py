import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from typer.testing import CliRunner
from src.main import app

runner = CliRunner()


def _response(status_code: int, payload, text: str = "ok") -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.text = text
    mock.json.return_value = payload
    return mock


TRACK_PAYLOAD = {
    "idTrack": 1,
    "title": "Bohemian Rhapsody",
    "youtubeLink": "https://www.youtube.com/watch?v=fJ9rUzIMt7o",
    "listeningCount": 42,
    "durationSeconds": 354,
    "createdAt": "2024-01-01T00:00:00",
    "artists": [],
    "status": "ok",
}


def _make_auth_patches():
    return (
        patch("requests.request"),
        patch("src.utils.http_client.get_access_token", return_value="access-token"),
        patch("src.utils.http_client.get_refresh_token", return_value="refresh-token"),
    )


# ─── track like <id> ──────────────────────────────────────────────────────────


class TestLikeCommand:
    def test_like_success(self):
        """Like un track avec succès."""
        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
        ):

            def _dispatch(method, **kwargs):
                url = kwargs.get("url", "")
                if method.upper() == "GET" and "/tracks/1" in url and "like" not in url:
                    return _response(200, TRACK_PAYLOAD)
                if method.upper() == "GET" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": False})
                if method.upper() == "POST" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": True})
                raise AssertionError(f"Unexpected: {method} {url}")

            mock_req.side_effect = _dispatch
            result = runner.invoke(app, ["track", "like", "1"])

        assert result.exit_code == 0
        assert "Bohemian Rhapsody" in result.output
        assert "liked" in result.output.lower() or "✓" in result.output

    def test_like_track_not_found(self):
        """Affiche une erreur si le track n'existe pas."""
        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
        ):
            mock_req.return_value = _response(404, {"detail": "Not found"}, "Not found")
            result = runner.invoke(app, ["track", "like", "9999"])

        assert result.exit_code == 0
        assert "✗" in result.output or "Error" in result.output

    def test_like_already_liked(self):
        """Affiche une erreur si le track est déjà liké."""
        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
        ):

            def _dispatch(method, **kwargs):
                url = kwargs.get("url", "")
                if method.upper() == "GET" and "/tracks/1" in url and "like" not in url:
                    return _response(200, TRACK_PAYLOAD)
                if method.upper() == "GET" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": True})
                raise AssertionError(f"Unexpected: {method} {url}")

            mock_req.side_effect = _dispatch
            result = runner.invoke(app, ["track", "like", "1"])

        assert result.exit_code == 0
        assert "✗" in result.output or "already" in result.output.lower()

    def test_like_api_error(self):
        """Affiche une erreur en cas d'erreur API inattendue."""
        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
        ):

            def _dispatch(method, **kwargs):
                url = kwargs.get("url", "")
                if method.upper() == "GET" and "/tracks/1" in url and "like" not in url:
                    return _response(200, TRACK_PAYLOAD)
                if method.upper() == "GET" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": False})
                if method.upper() == "POST" and "/tracks/1/like" in url:
                    return _response(500, {"detail": "Server error"}, "Server error")
                raise AssertionError(f"Unexpected: {method} {url}")

            mock_req.side_effect = _dispatch
            result = runner.invoke(app, ["track", "like", "1"])

        assert result.exit_code == 0
        assert "✗" in result.output or "Error" in result.output


# ─── track unlike <id> ────────────────────────────────────────────────────────


class TestUnlikeCommand:
    def test_unlike_success(self):
        """Unlike un track avec succès."""
        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
        ):

            def _dispatch(method, **kwargs):
                url = kwargs.get("url", "")
                if method.upper() == "GET" and "/tracks/1" in url and "like" not in url:
                    return _response(200, TRACK_PAYLOAD)
                if method.upper() == "GET" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": True})
                if method.upper() == "DELETE" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": False})
                raise AssertionError(f"Unexpected: {method} {url}")

            mock_req.side_effect = _dispatch
            result = runner.invoke(app, ["track", "unlike", "1"])

        assert result.exit_code == 0
        assert "Bohemian Rhapsody" in result.output
        assert "✓" in result.output

    def test_unlike_not_liked(self):
        """Affiche une erreur si le track n'est pas liké."""
        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
        ):

            def _dispatch(method, **kwargs):
                url = kwargs.get("url", "")
                if method.upper() == "GET" and "/tracks/1" in url and "like" not in url:
                    return _response(200, TRACK_PAYLOAD)
                if method.upper() == "GET" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": False})
                raise AssertionError(f"Unexpected: {method} {url}")

            mock_req.side_effect = _dispatch
            result = runner.invoke(app, ["track", "unlike", "1"])

        assert result.exit_code == 0
        assert "✗" in result.output or "not in" in result.output.lower()

    def test_unlike_track_not_found(self):
        """Affiche une erreur si le track n'existe pas."""
        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
        ):
            mock_req.return_value = _response(404, {"detail": "Not found"}, "Not found")
            result = runner.invoke(app, ["track", "unlike", "9999"])

        assert result.exit_code == 0
        assert "✗" in result.output or "Error" in result.output

    def test_unlike_api_error(self):
        """Affiche une erreur en cas d'erreur API inattendue."""
        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
        ):

            def _dispatch(method, **kwargs):
                url = kwargs.get("url", "")
                if method.upper() == "GET" and "/tracks/1" in url and "like" not in url:
                    return _response(200, TRACK_PAYLOAD)
                if method.upper() == "GET" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": True})
                if method.upper() == "DELETE" and "/tracks/1/like" in url:
                    return _response(500, {"detail": "Server error"}, "Server error")
                raise AssertionError(f"Unexpected: {method} {url}")

            mock_req.side_effect = _dispatch
            result = runner.invoke(app, ["track", "unlike", "1"])

        assert result.exit_code == 0
        assert "✗" in result.output or "Error" in result.output


# ─── track like-current ───────────────────────────────────────────────────────


class TestLikeCurrentCommand:
    def test_like_current_success(self, tmp_path):
        """Like le track en cours de lecture avec succès."""
        pid_file = tmp_path / "yt-player.pid"
        current_file = tmp_path / "yt-current-track"
        pid_file.write_text("12345")
        current_file.write_text("1")

        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
            patch("src.services.like.PID_FILE", pid_file),
            patch("src.services.like.CURRENT_TRACK_FILE", current_file),
            patch("psutil.pid_exists", return_value=True),
        ):

            def _dispatch(method, **kwargs):
                url = kwargs.get("url", "")
                if method.upper() == "GET" and "/tracks/1" in url and "like" not in url:
                    return _response(200, TRACK_PAYLOAD)
                if method.upper() == "GET" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": False})
                if method.upper() == "POST" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": True})
                raise AssertionError(f"Unexpected: {method} {url}")

            mock_req.side_effect = _dispatch
            result = runner.invoke(app, ["track", "like-current"])

        assert result.exit_code == 0
        assert "Bohemian Rhapsody" in result.output
        assert "✓" in result.output

    def test_like_current_no_player_running(self, tmp_path):
        """Affiche une erreur si aucun track n'est en cours de lecture."""
        pid_file = tmp_path / "yt-player.pid"  # does not exist

        with (
            patch("src.services.like.PID_FILE", pid_file),
        ):
            result = runner.invoke(app, ["track", "like-current"])

        assert result.exit_code == 0
        assert "✗" in result.output
        assert "playing" in result.output.lower() or "No track" in result.output

    def test_like_current_player_stopped(self, tmp_path):
        """Affiche une erreur si le processus player est mort (PID obsolète)."""
        pid_file = tmp_path / "yt-player.pid"
        pid_file.write_text("99999")

        with (
            patch("src.services.like.PID_FILE", pid_file),
            patch("psutil.pid_exists", return_value=False),
        ):
            result = runner.invoke(app, ["track", "like-current"])

        assert result.exit_code == 0
        assert "✗" in result.output
        assert "stopped" in result.output.lower() or "playing" in result.output.lower()

    def test_like_current_no_track_file(self, tmp_path):
        """Affiche une erreur si le fichier de track courant est absent."""
        pid_file = tmp_path / "yt-player.pid"
        current_file = tmp_path / "yt-current-track"  # does not exist
        pid_file.write_text("12345")

        with (
            patch("src.services.like.PID_FILE", pid_file),
            patch("src.services.like.CURRENT_TRACK_FILE", current_file),
            patch("psutil.pid_exists", return_value=True),
        ):
            result = runner.invoke(app, ["track", "like-current"])

        assert result.exit_code == 0
        assert "✗" in result.output
        assert "determine" in result.output.lower() or "Cannot" in result.output

    def test_like_current_already_liked(self, tmp_path):
        """Affiche une erreur si le track en cours est déjà liké."""
        pid_file = tmp_path / "yt-player.pid"
        current_file = tmp_path / "yt-current-track"
        pid_file.write_text("12345")
        current_file.write_text("1")

        with (
            patch("requests.request") as mock_req,
            patch("src.utils.http_client.get_access_token", return_value="token"),
            patch("src.utils.http_client.get_refresh_token", return_value="refresh"),
            patch("src.services.like.PID_FILE", pid_file),
            patch("src.services.like.CURRENT_TRACK_FILE", current_file),
            patch("psutil.pid_exists", return_value=True),
        ):

            def _dispatch(method, **kwargs):
                url = kwargs.get("url", "")
                if method.upper() == "GET" and "/tracks/1" in url and "like" not in url:
                    return _response(200, TRACK_PAYLOAD)
                if method.upper() == "GET" and "/tracks/1/like" in url:
                    return _response(200, {"trackId": 1, "isLiked": True})
                raise AssertionError(f"Unexpected: {method} {url}")

            mock_req.side_effect = _dispatch
            result = runner.invoke(app, ["track", "like-current"])

        assert result.exit_code == 0
        assert "✗" in result.output
        assert "already" in result.output.lower()
