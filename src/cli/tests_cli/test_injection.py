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


def test_bash_playlist_add_track_url(mock_api_calls):
    """Test bash injection on the URL of a track"""
    payload = "https://youtube.com/watch?v=abc; whoami"

    # Mock la réponse d'ajout de track
    mock_api_calls["responses"]["post"].json.return_value = {
        "idTrack": 1,
        "title": "test",
        "youtubeLink": payload,
        "durationSeconds": 180,
        "artists": [],
    }

    # Mock for get_playlist and get_playlist_tracks
    mock_api_calls["responses"]["get"].json.side_effect = [
        {
            "idPlaylist": 2,
            "name": "Test",
            "vote": 0,
            "createdAt": "2024-01-01T00:00:00",
            "idGenre": 1,
            "visibility": "PUBLIC",
        },
        [
            {
                "idTrack": 1,
                "title": "test",
                "youtubeLink": payload,
                "durationSeconds": 180,
                "artists": [],
            }
        ],
    ]

    result = runner.invoke(
        app,
        ["playlist", "add-track", "1", "--url", payload, "--title", "test"],
    )

    assert mock_api_calls["request"].called
    assert_no_system_execution(result)


def test_bash_playlist_add_track_title(mock_api_calls):
    """Test bash injection on the title of a track"""
    payload = "TestTrack | whoami"

    # Mock the response of adding track
    mock_api_calls["responses"]["post"].json.return_value = {
        "idTrack": 2,
        "title": payload,
        "youtubeLink": "https://youtube.com/watch?v=abc",
        "durationSeconds": 180,
        "artists": [],
    }

    # Mock the get_playlist and get_playlist_tracks responses
    mock_api_calls["responses"]["get"].json.side_effect = [
        {
            "idPlaylist": 2,
            "name": "Test",
            "vote": 0,
            "createdAt": "2024-01-01T00:00:00",
            "idGenre": 1,
            "visibility": "PUBLIC",
        },
        [
            {
                "idTrack": 1,
                "title": payload,
                "youtubeLink": "https://youtube.com/watch?v=abc",
                "durationSeconds": 180,
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
            "https://youtube.com/watch?v=abc",
            "--title",
            payload,
        ],
    )

    assert mock_api_calls["request"].called
    assert_no_system_execution(result)
