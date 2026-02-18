from unittest.mock import MagicMock, patch

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.playlist import (
    add_track_to_playlist,
    delete_playlist,
    get_all_playlists,
    get_playlist,
    search_playlists,
    update_playlist,
)


def _response(status_code: int, payload, text: str = "ok") -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = payload
    return response


@pytest.fixture()
def mock_auth_and_http():
    with (
        patch("requests.request") as mock_request,
        patch("src.utils.http_client.get_access_token", return_value="access-token"),
        patch("src.utils.http_client.get_refresh_token", return_value="refresh-token"),
        patch("src.services.playlist.auth_service.whoami", return_value={"id": 1}),
    ):
        yield mock_request


def test_get_all_playlists_accessible_scope_filters_visibility(mock_auth_and_http):
    payload = [
        {
            "idPlaylist": 1,
            "name": "mine-private",
            "idGenre": 1,
            "idOwner": 1,
            "vote": 0,
            "visibility": "PRIVATE",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
        {
            "idPlaylist": 2,
            "name": "mine-open",
            "idGenre": 1,
            "idOwner": 1,
            "vote": 0,
            "visibility": "OPEN",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
        {
            "idPlaylist": 3,
            "name": "other-open",
            "idGenre": 1,
            "idOwner": 2,
            "vote": 0,
            "visibility": "OPEN",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
        {
            "idPlaylist": 4,
            "name": "other-public",
            "idGenre": 1,
            "idOwner": 3,
            "vote": 0,
            "visibility": "PUBLIC",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
        {
            "idPlaylist": 5,
            "name": "other-private",
            "idGenre": 1,
            "idOwner": 4,
            "vote": 0,
            "visibility": "PRIVATE",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
    ]
    mock_auth_and_http.return_value = _response(200, payload)

    playlists = get_all_playlists("accessible")
    ids = {playlist.idPlaylist for playlist in playlists}

    assert ids == {1, 2, 3, 4}


def test_get_all_playlists_scopes(mock_auth_and_http):
    payload = [
        {
            "idPlaylist": 11,
            "name": "mine-private",
            "idGenre": 1,
            "idOwner": 1,
            "vote": 0,
            "visibility": "PRIVATE",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
        {
            "idPlaylist": 12,
            "name": "other-open",
            "idGenre": 1,
            "idOwner": 2,
            "vote": 0,
            "visibility": "OPEN",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
        {
            "idPlaylist": 13,
            "name": "other-public",
            "idGenre": 1,
            "idOwner": 3,
            "vote": 0,
            "visibility": "PUBLIC",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
    ]
    mock_auth_and_http.return_value = _response(200, payload)

    mine = get_all_playlists("mine")
    open_playlists = get_all_playlists("open")
    public = get_all_playlists("public")

    assert [playlist.idPlaylist for playlist in mine] == [11]
    assert [playlist.idPlaylist for playlist in open_playlists] == [12]
    assert [playlist.idPlaylist for playlist in public] == [13]


def test_get_playlist_denies_other_private_playlist(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(
        200,
        {
            "idPlaylist": 20,
            "name": "hidden",
            "idGenre": 1,
            "idOwner": 9,
            "vote": 0,
            "visibility": "PRIVATE",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
    )

    with pytest.raises(Exception, match="permission to access"):
        get_playlist("20")


def test_update_denies_open_playlist_if_not_owner(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(
        200,
        {
            "idPlaylist": 30,
            "name": "open-other",
            "idGenre": 1,
            "idOwner": 2,
            "vote": 0,
            "visibility": "OPEN",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
    )

    with pytest.raises(Exception, match="permission to edit"):
        update_playlist("30", name="new-name")


def test_delete_allows_owner(mock_auth_and_http):
    def _dispatch(method: str, **kwargs):
        url = kwargs["url"]
        if method.upper() == "GET" and url.endswith("/playlists/31"):
            return _response(
                200,
                {
                    "idPlaylist": 31,
                    "name": "mine-open",
                    "idGenre": 1,
                    "idOwner": 1,
                    "vote": 0,
                    "visibility": "OPEN",
                    "coverImage": None,
                    "createdAt": "2024-01-01T00:00:00",
                    "updatedAt": "2024-01-01T00:00:00",
                },
            )
        if method.upper() == "DELETE" and url.endswith("/playlists/31"):
            return _response(200, {"message": "ok"})
        raise AssertionError(f"Unexpected request: {method} {url}")

    mock_auth_and_http.side_effect = _dispatch

    result = delete_playlist("31")

    assert result["message"] == "ok"


def test_add_track_denies_non_owner_open_playlist(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(
        200,
        {
            "idPlaylist": 40,
            "name": "other-open",
            "idGenre": 1,
            "idOwner": 2,
            "vote": 0,
            "visibility": "OPEN",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
    )

    with pytest.raises(Exception, match="permission to edit"):
        add_track_to_playlist("40", "new-track", "https://youtu.be/abc")


def test_search_playlists_excludes_other_private(mock_auth_and_http):
    payload = [
        {
            "idPlaylist": 50,
            "name": "my secret mix",
            "idGenre": 1,
            "idOwner": 1,
            "vote": 0,
            "visibility": "PRIVATE",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
        {
            "idPlaylist": 51,
            "name": "secret open room",
            "idGenre": 1,
            "idOwner": 2,
            "vote": 0,
            "visibility": "OPEN",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
        {
            "idPlaylist": 52,
            "name": "secret private room",
            "idGenre": 1,
            "idOwner": 3,
            "vote": 0,
            "visibility": "PRIVATE",
            "coverImage": None,
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00",
        },
    ]
    mock_auth_and_http.return_value = _response(200, payload)

    results = search_playlists("secret")
    ids = {playlist.idPlaylist for playlist in results}

    assert ids == {50, 51}
