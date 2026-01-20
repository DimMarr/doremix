import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typer.testing import CliRunner
from src.main import app

# IMPORTANT : Importez Base et SessionLocal depuis votre fichier de config DB
# Adaptez le chemin si nécessaire (ex: from src.database import ...)
from database import Base, SessionLocal


# 1. On prépare une DB SQLite en mémoire (rapide et isolée)
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def override_db():
    """
    This fixture runs automatically before EVERY test in this file.
    It replaces the real DB with the test DB.
    """
    # Empty tables before test
    Base.metadata.create_all(bind=test_engine)

    # Patching SessionLocal to use the testing session
    with patch("database.SessionLocal", return_value=TestingSessionLocal()):
        yield

    # Cleaning
    Base.metadata.drop_all(bind=test_engine)


# ---------------------------------------------------

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
    for forbidden in FORBIDDEN_OUTPUTS:
        assert forbidden not in result.output


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
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
        ["playlist", "add-track", "1", "--url", payload, "--title", "test"],
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
