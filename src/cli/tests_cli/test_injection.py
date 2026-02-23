import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app

runner = CliRunner()

BASH_PAYLOADS = [
    "; whoami",
    "&& whoami",
    "| whoami",
    "$(whoami)",
    "`whoami`",
    "; sleep 3",
    "> /tmp/pwned",
]

FORBIDDEN_OUTPUTS = ["uid=", "gid=", "root:", "/bin/", "/usr/bin"]

VALID_YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

VALID_YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "http://youtube.com/watch?v=dQw4w9WgXcQ",
    "http://youtu.be/dQw4w9WgXcQ",
    "http://www.youtube.com/embed/dQw4w9WgXcQ",
]

INVALID_YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120",  # Paramètres supplémentaires
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLtest",  # Paramètres supplémentaires
    "https://www.youtube.com/watch?v=abc",  # ID trop court
    "https://www.youtube.com/watch?v=abcdefghijklmno",  # ID trop long
    "https://vimeo.com/123456789",  # Pas YouTube
    "https://dailymotion.com/video/x123456",  # Pas YouTube
    "https://www.youtube.com/",  # Pas de vidéo
    "https://www.youtube.com/watch",  # Pas d'ID
    "https://www.youtube.com/watch?v=",  # ID vide
    "youtube.com/watch?v=dQw4w9WgXcQ",  # Pas de protocole
    "https://www.youtubee.com/watch?v=dQw4w9WgXcQ",  # Typo dans le domaine
    "https://www.youtube.com/watchh?v=dQw4w9WgXcQ",  # Typo dans le path
    "not_a_url",  # Pas une URL
    "",  # Vide
]


def assert_no_system_execution(result):
    """Verify that no system command execution traces are present in the output."""
    for forbidden in FORBIDDEN_OUTPUTS:
        assert (
            forbidden not in result.output
        ), f"⚠️  Possible system execution : '{forbidden}' find in output."


@pytest.fixture(autouse=True)
def mock_api_calls():
    """
    Mock every API call to prevent real HTTP requests during tests.
    """
    with (
        patch("requests.request") as mock_request,
        patch("src.utils.http_client.get_access_token", return_value="access-token"),
        patch("src.utils.http_client.get_refresh_token", return_value="refresh-token"),
        patch("src.services.playlist.auth_service.whoami", return_value={"id": 1}),
    ):
        responses: dict[str, MagicMock] = {}
        for method in ("get", "post", "patch", "delete"):
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = []
            response.text = "ok"
            responses[method] = response

        def _request_dispatch(method: str, **kwargs):
            return responses[method.lower()]

        mock_request.side_effect = _request_dispatch

        yield {"request": mock_request, "responses": responses}


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
def test_bash_playlist_search(payload, mock_api_calls):
    """Test bash injection on playlist search"""
    # Configuration du mock pour retourner des playlists vides
    mock_api_calls["responses"]["get"].json.return_value = []

    result = runner.invoke(app, ["playlist", "search", payload])

    # Vérifier que l'appel API a été fait
    assert mock_api_calls["request"].called

    # Vérifier qu'aucune commande système n'a été exécutée
    assert_no_system_execution(result)


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
def test_bash_playlist_search_tracks(payload, mock_api_calls):
    """Test bash injection on the search of tracks in a playlist"""
    # Mock pour retourner une playlist valide puis des tracks vides
    mock_api_calls["responses"]["get"].json.side_effect = [
        {
            "idPlaylist": 2,
            "name": "Test",
            "vote": 0,
            "createdAt": "2024-01-01T00:00:00",
            "idGenre": 1,
            "visibility": "PUBLIC",
        },
        [],
    ]

    result = runner.invoke(app, ["playlist", "search-tracks", "1", payload])

    assert mock_api_calls["request"].called
    assert_no_system_execution(result)


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
def test_bash_track_search(payload, mock_api_calls):
    """Test bash injection on the search of tracks"""
    mock_api_calls["responses"]["get"].json.return_value = []

    result = runner.invoke(app, ["track", "search", payload])

    assert mock_api_calls["request"].called
    assert_no_system_execution(result)


def test_bash_playlist_create_name(mock_api_calls):
    """Test bash injection on the name of playlist at creation"""
    payload = "MyPlaylist; whoami"

    # Mock la réponse de création
    mock_api_calls["responses"]["post"].json.return_value = {
        "idPlaylist": 2,
        "name": payload,
        "vote": 0,
        "createdAt": "2024-01-01T00:00:00",
        "updatedAt": "2024-01-01T00:00:00",
        "idGenre": 1,
        "visibility": "PUBLIC",
    }

    result = runner.invoke(app, ["playlist", "create", "--name", payload])

    assert mock_api_calls["request"].called
    assert_no_system_execution(result)


def test_bash_playlist_update_name(mock_api_calls):
    """Test bash injection on the name of playlist at modification"""
    payload = "UpdatedPlaylist && whoami"

    # Mock la réponse de mise à jour
    mock_api_calls["responses"]["patch"].json.return_value = {
        "idPlaylist": 2,
        "name": payload,
        "vote": 0,
        "createdAt": "2024-01-01T00:00:00",
        "updatedAt": "2024-01-01T00:00:00",
        "idGenre": 1,
        "visibility": "PUBLIC",
    }

    result = runner.invoke(app, ["playlist", "update", "1", "--name", payload])

    assert mock_api_calls["request"].called
    assert_no_system_execution(result)


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
def test_bash_playlist_add_track_url_injection(payload, mock_api_calls):
    """Test bash injection on the URL of a track - should be rejected by validation"""
    invalid_url = f"https://youtube.com/watch?v=abc{payload}"

    result = runner.invoke(
        app,
        ["playlist", "add-track", "1", "--url", invalid_url, "--title", "test"],
    )

    # La validation YouTube doit rejeter ce lien
    assert "Invalid YouTube link" in result.output
    assert_no_system_execution(result)


def test_bash_playlist_add_track_title(mock_api_calls):
    """Test bash injection on the title of a track"""
    payload = "TestTrack | whoami"

    # Mock the response of adding track
    mock_api_calls["responses"]["post"].json.return_value = {
        "idTrack": 2,
        "title": payload,
        "youtubeLink": VALID_YOUTUBE_URL,
        "durationSeconds": 180,
        "listeningCount": 0,
        "createdAt": "2024-01-01T00:00:00",
        "artists": [],
    }

    # Mock the get_playlist and get_playlist_tracks responses
    mock_api_calls["responses"]["get"].json.side_effect = [
        {
            "idPlaylist": 2,
            "name": "Test",
            "vote": 0,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
            "idGenre": 1,
            "idOwner": 1,
            "visibility": "PUBLIC",
        },
        [
            {
                "idTrack": 1,
                "title": payload,
                "youtubeLink": VALID_YOUTUBE_URL,
                "durationSeconds": 180,
                "listeningCount": 0,
                "createdAt": "2024-01-01T00:00:00",
                "artists": [],
            }
        ],
    ]

    result = runner.invoke(
        app,
        [
            "playlist",
            "add-track",
            "1",
            "--url",
            VALID_YOUTUBE_URL,
            "--title",
            payload,
        ],
    )

    assert mock_api_calls["request"].called
    assert_no_system_execution(result)


def test_valid_youtube_url_accepted(mock_api_calls):
    """Test that valid YouTube URLs are accepted"""
    # Mock the response of adding track
    mock_api_calls["responses"]["post"].json.return_value = {
        "idTrack": 1,
        "title": "Test Track",
        "youtubeLink": VALID_YOUTUBE_URL,
        "durationSeconds": 180,
        "listeningCount": 0,
        "createdAt": "2024-01-01T00:00:00",
        "artists": [],
    }

    # Mock the get_playlist and get_playlist_tracks responses
    mock_api_calls["responses"]["get"].json.side_effect = [
        {
            "idPlaylist": 2,
            "name": "Test",
            "vote": 0,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
            "idGenre": 1,
            "idOwner": 1,
            "visibility": "PUBLIC",
        },
        [
            {
                "idTrack": 1,
                "title": "Test Track",
                "youtubeLink": VALID_YOUTUBE_URL,
                "durationSeconds": 180,
                "listeningCount": 0,
                "createdAt": "2024-01-01T00:00:00",
                "artists": [],
            }
        ],
    ]

    result = runner.invoke(
        app,
        [
            "playlist",
            "add-track",
            "1",
            "--url",
            VALID_YOUTUBE_URL,
            "--title",
            "Test Track",
        ],
    )

    assert mock_api_calls["request"].called
    assert "Invalid YouTube link" not in result.output
    assert_no_system_execution(result)


@pytest.mark.parametrize("valid_url", VALID_YOUTUBE_URLS)
def test_add_track_accepts_valid_youtube_urls(valid_url, mock_api_calls):
    """Test that all valid YouTube URL formats are accepted"""
    # Mock the response of adding track
    mock_api_calls["responses"]["post"].json.return_value = {
        "idTrack": 1,
        "title": "Test Track",
        "youtubeLink": valid_url,
        "durationSeconds": 180,
        "listeningCount": 0,
        "createdAt": "2024-01-01T00:00:00",
        "artists": [],
    }

    # Mock the get_playlist and get_playlist_tracks responses
    mock_api_calls["responses"]["get"].json.side_effect = [
        {
            "idPlaylist": 1,
            "name": "Test Playlist",
            "vote": 0,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
            "idGenre": 1,
            "idOwner": 1,
            "visibility": "PUBLIC",
        },
        [
            {
                "idTrack": 1,
                "title": "Test Track",
                "youtubeLink": valid_url,
                "durationSeconds": 180,
                "listeningCount": 0,
                "createdAt": "2024-01-01T00:00:00",
                "artists": [],
            }
        ],
    ]

    result = runner.invoke(
        app,
        [
            "playlist",
            "add-track",
            "1",
            "--url",
            valid_url,
            "--title",
            "Test Track",
        ],
    )

    assert (
        "Invalid YouTube link" not in result.output
    ), f"URL should be valid: {valid_url}"
    assert_no_system_execution(result)


@pytest.mark.parametrize("invalid_url", INVALID_YOUTUBE_URLS)
def test_add_track_rejects_invalid_youtube_urls(invalid_url, mock_api_calls):
    """Test that all invalid YouTube URL formats are rejected"""
    result = runner.invoke(
        app,
        [
            "playlist",
            "add-track",
            "1",
            "--url",
            invalid_url,
            "--title",
            "Test Track",
        ],
    )

    assert (
        "Invalid YouTube link" in result.output
    ), f"URL should be invalid: {invalid_url}"
    assert_no_system_execution(result)


def test_add_track_rejects_url_with_extra_parameters(mock_api_calls):
    """Test that YouTube URLs with extra parameters are rejected"""
    urls_with_params = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLtest123",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&index=5",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120&list=PLtest",
        "https://youtu.be/dQw4w9WgXcQ?t=120",
        "https://youtu.be/dQw4w9WgXcQ?si=abc123",
    ]

    for url in urls_with_params:
        result = runner.invoke(
            app,
            [
                "playlist",
                "add-track",
                "1",
                "--url",
                url,
                "--title",
                "Test Track",
            ],
        )

        assert (
            "Invalid YouTube link" in result.output
        ), f"URL with params should be rejected: {url}"
        assert_no_system_execution(result)


def test_add_track_rejects_non_youtube_video_platforms(mock_api_calls):
    """Test that non-YouTube video platform URLs are rejected"""
    non_youtube_urls = [
        "https://vimeo.com/123456789",
        "https://dailymotion.com/video/x123456",
        "https://twitch.tv/videos/123456789",
        "https://facebook.com/watch?v=123456789",
        "https://tiktok.com/@user/video/123456789",
    ]

    for url in non_youtube_urls:
        result = runner.invoke(
            app,
            [
                "playlist",
                "add-track",
                "1",
                "--url",
                url,
                "--title",
                "Test Track",
            ],
        )

        assert (
            "Invalid YouTube link" in result.output
        ), f"Non-YouTube URL should be rejected: {url}"
        assert_no_system_execution(result)


def test_add_track_rejects_malformed_youtube_urls(mock_api_calls):
    """Test that malformed YouTube URLs are rejected"""
    malformed_urls = [
        "https://www.youtube.com/watch?v=",  # Empty video ID
        "https://www.youtube.com/watch?v=abc",  # Too short video ID
        "https://www.youtube.com/watch?v=abcdefghijklmnop",  # Too long video ID
        "https://www.youtube.com/watch",  # Missing video ID parameter
        "https://www.youtube.com/",  # No path
        "https://youtu.be/",  # Empty short URL
        "https://youtu.be/abc",  # Too short video ID
        "www.youtube.com/watch?v=dQw4w9WgXcQ",  # Missing protocol
        "youtube.com/watch?v=dQw4w9WgXcQ",  # Missing protocol
    ]

    for url in malformed_urls:
        result = runner.invoke(
            app,
            [
                "playlist",
                "add-track",
                "1",
                "--url",
                url,
                "--title",
                "Test Track",
            ],
        )

        assert (
            "Invalid YouTube link" in result.output
        ), f"Malformed URL should be rejected: {url}"
        assert_no_system_execution(result)


def test_add_track_rejects_youtube_lookalike_domains(mock_api_calls):
    """Test that YouTube lookalike domains are rejected"""
    lookalike_urls = [
        "https://www.youtubee.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.org/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.net/watch?v=dQw4w9WgXcQ",
        "https://www.youtubecom.com/watch?v=dQw4w9WgXcQ",
        "https://www.fakeyoutube.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.malicious.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.bee/dQw4w9WgXcQ",
    ]

    for url in lookalike_urls:
        result = runner.invoke(
            app,
            [
                "playlist",
                "add-track",
                "1",
                "--url",
                url,
                "--title",
                "Test Track",
            ],
        )

        assert (
            "Invalid YouTube link" in result.output
        ), f"Lookalike URL should be rejected: {url}"
        assert_no_system_execution(result)
