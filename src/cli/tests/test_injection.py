import pytest
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()

# Payloads for testing command injection via bash syntax
BASH_PAYLOADS = [
    "; whoami",
    "&& whoami",
    "| whoami",
    "$(whoami)",
    "`whoami`",
    "; sleep 3",
    "> /tmp/pwned",
]

# Signs of system command execution to look for in outputs
FORBIDDEN_OUTPUTS = [
    "uid=",
    "gid=",
    "root:",
    "/bin/",
    "/usr/bin",
]


def assert_no_system_execution(result):
    """
    Verify that the command output does not contain any signs of system command execution.
    """
    for forbidden in FORBIDDEN_OUTPUTS:
        assert forbidden not in result.output


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
# Pytest will run the test once per payload value.
def test_bash_playlist_search(payload):
    result = runner.invoke(app, ["playlist", "search", payload])
    assert result.exit_code == 0
    assert_no_system_execution(result)


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
def test_bash_playlist_search_tracks(payload):
    result = runner.invoke(app, ["playlist", "search-tracks", "1", payload])
    assert result.exit_code == 0
    assert_no_system_execution(result)


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
def test_bash_track_search(payload):
    result = runner.invoke(app, ["track", "search", payload])
    assert result.exit_code == 0
    assert_no_system_execution(result)


def test_bash_playlist_create_name():
    payload = "MyPlaylist; whoami"
    result = runner.invoke(app, ["playlist", "create", "--name", payload])
    assert result.exit_code == 0
    assert_no_system_execution(result)


def test_bash_playlist_update_name():
    payload = "UpdatedPlaylist && whoami"
    result = runner.invoke(app, ["playlist", "update", "1", "--name", payload])
    assert result.exit_code == 0
    assert_no_system_execution(result)


def test_bash_playlist_add_track_url():
    payload = "https://youtube.com/watch?v=abc; whoami"
    result = runner.invoke(
        app,
        [
            "playlist",
            "add-track",
            "1",
            "--url",
            payload,
            "--title",
            "test",
        ],
    )
    assert result.exit_code == 0
    assert_no_system_execution(result)


def test_bash_playlist_add_track_title():
    payload = "TestTrack | whoami"
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
    assert result.exit_code == 0
    assert_no_system_execution(result)
