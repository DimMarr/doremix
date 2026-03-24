from unittest.mock import MagicMock, patch

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.exceptions import NotAuthenticatedError, PlaylistNotFoundError
from src.services.admin_playlist import (
    get_all_playlists,
    get_playlist_tracks,
    update_playlist,
    delete_playlist,
    add_track,
    remove_track,
)


def _response(status_code: int, payload, text: str = "ok") -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = payload
    return response


PLAYLIST_PAYLOAD = {
    "idPlaylist": 1,
    "name": "Test Playlist",
    "idGenre": 2,
    "idOwner": 10,
    "vote": 0,
    "visibility": "PUBLIC",
    "coverImage": None,
    "createdAt": "2024-01-01T00:00:00",
    "updatedAt": "2024-01-01T00:00:00",
}

TRACK_PAYLOAD = {
    "idTrack": 42,
    "title": "Test Track",
    "youtubeLink": "https://youtube.com/watch?v=abc",
    "listeningCount": 0,
    "durationSeconds": 210,
    "createdAt": "2024-01-01T00:00:00",
    "artists": [],
}


@pytest.fixture()
def mock_auth_and_http():
    with (
        patch("requests.request") as mock_request,
        patch("src.utils.http_client.get_access_token", return_value="access-token"),
        patch("src.utils.http_client.get_refresh_token", return_value="refresh-token"),
        patch(
            "src.utils.http_client.auth_service.refresh",
            side_effect=NotAuthenticatedError("Session expired"),
        ),
    ):
        yield mock_request


# --- get_all_playlists ---


def test_get_all_playlists_success(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, [PLAYLIST_PAYLOAD])
    playlists = get_all_playlists()
    assert len(playlists) == 1
    assert playlists[0].idPlaylist == 1
    assert playlists[0].name == "Test Playlist"


def test_get_all_playlists_empty(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, [])
    assert get_all_playlists() == []


def test_get_all_playlists_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")
    with pytest.raises(Exception, match="Session expired"):
        get_all_playlists()


def test_get_all_playlists_raises_on_403(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(403, {}, text="Forbidden")
    with pytest.raises(Exception, match="Access denied"):
        get_all_playlists()


# --- get_playlist_tracks ---


def test_get_playlist_tracks_success(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, [TRACK_PAYLOAD])
    tracks = get_playlist_tracks(1)
    assert len(tracks) == 1
    assert tracks[0].idTrack == 42
    assert tracks[0].title == "Test Track"


def test_get_playlist_tracks_empty(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, [])
    assert get_playlist_tracks(1) == []


def test_get_playlist_tracks_raises_on_404(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(404, {}, text="Not Found")
    with pytest.raises(PlaylistNotFoundError, match="not found"):
        get_playlist_tracks(999)


def test_get_playlist_tracks_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")
    with pytest.raises(Exception, match="Session expired"):
        get_playlist_tracks(1)


# --- update_playlist ---


def test_update_playlist_success(mock_auth_and_http):
    updated = {**PLAYLIST_PAYLOAD, "name": "Updated Name"}
    mock_auth_and_http.return_value = _response(200, updated)
    result = update_playlist(1, name="Updated Name")
    assert result.name == "Updated Name"
    assert result.idPlaylist == 1


def test_update_playlist_raises_on_404(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(404, {}, text="Not Found")
    with pytest.raises(PlaylistNotFoundError, match="not found"):
        update_playlist(999, name="Ghost")


def test_update_playlist_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")
    with pytest.raises(Exception, match="Session expired"):
        update_playlist(1, visibility="PUBLIC")


# --- delete_playlist ---


def test_delete_playlist_success_on_200(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, {"message": "Deleted"})
    result = delete_playlist(1)
    assert result == {"message": "Deleted"}


def test_delete_playlist_success_on_204(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(204, None)
    result = delete_playlist(1)
    assert result == {}


def test_delete_playlist_raises_on_404(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(404, {}, text="Not Found")
    with pytest.raises(PlaylistNotFoundError, match="not found"):
        delete_playlist(999)


def test_delete_playlist_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")
    with pytest.raises(Exception, match="Session expired"):
        delete_playlist(1)


# --- add_track ---


def test_add_track_success(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, TRACK_PAYLOAD)
    track = add_track(1, title="Test Track", url="https://youtube.com/watch?v=abc")
    assert track.idTrack == 42
    assert track.title == "Test Track"


def test_add_track_raises_on_404(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(404, {}, text="Not Found")
    with pytest.raises(PlaylistNotFoundError, match="not found"):
        add_track(999, title="Ghost", url="https://youtube.com/watch?v=xyz")


def test_add_track_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")
    with pytest.raises(Exception, match="Session expired"):
        add_track(1, title="Track", url="https://youtube.com/watch?v=abc")


def test_add_track_raises_on_403(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(403, {}, text="Forbidden")
    with pytest.raises(Exception, match="Access denied"):
        add_track(1, title="Track", url="https://youtube.com/watch?v=abc")


# --- remove_track ---


def test_remove_track_success(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, PLAYLIST_PAYLOAD)
    result = remove_track(1, 42)
    assert result.idPlaylist == 1


def test_remove_track_raises_on_404(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(404, {}, text="Not Found")
    with pytest.raises(PlaylistNotFoundError, match="not found"):
        remove_track(999, 42)


def test_remove_track_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")
    with pytest.raises(Exception, match="Session expired"):
        remove_track(1, 42)


def test_remove_track_raises_on_403(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(403, {}, text="Forbidden")
    with pytest.raises(Exception, match="Access denied"):
        remove_track(1, 42)
