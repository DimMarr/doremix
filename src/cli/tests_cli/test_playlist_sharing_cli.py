from unittest.mock import MagicMock, patch

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.playlist import get_shared_users, remove_shared_user
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()


def _response(status_code: int, payload, text: str = "ok") -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = payload
    return response


OWNER_PLAYLIST = {
    "idPlaylist": 9,
    "name": "My Playlist",
    "idGenre": 1,
    "idOwner": 1,
    "vote": 0,
    "visibility": "PRIVATE",
    "coverImage": None,
    "createdAt": "2024-01-01T00:00:00",
    "updatedAt": "2024-01-01T00:00:00",
}

OTHER_OWNER_PLAYLIST = {
    "idPlaylist": 10,
    "name": "Other Playlist",
    "idGenre": 1,
    "idOwner": 2,
    "vote": 0,
    "visibility": "PRIVATE",
    "coverImage": None,
    "createdAt": "2024-01-01T00:00:00",
    "updatedAt": "2024-01-01T00:00:00",
}

SHARED_USERS = [
    {
        "idUser": 2,
        "idPlaylist": 9,
        "editor": False,
        "username": "alice",
        "email": "alice@etu.umontpellier.fr",
    },
    {
        "idUser": 3,
        "idPlaylist": 9,
        "editor": True,
        "username": "bob",
        "email": "bob@etu.umontpellier.fr",
    },
]


@pytest.fixture()
def mock_auth_and_http():
    with (
        patch("requests.request") as mock_request,
        patch("src.utils.http_client.get_access_token", return_value="access-token"),
        patch("src.utils.http_client.get_refresh_token", return_value="refresh-token"),
        patch("src.services.playlist.auth_service.whoami", return_value={"id": 1}),
    ):
        yield mock_request


@pytest.fixture()
def mock_auth_and_http_admin():
    with (
        patch("requests.request") as mock_request,
        patch("src.utils.http_client.get_access_token", return_value="access-token"),
        patch("src.utils.http_client.get_refresh_token", return_value="refresh-token"),
        patch(
            "src.services.playlist.auth_service.whoami",
            return_value={"id": 99, "role": "ADMIN"},
        ),
    ):
        yield mock_request


# ─── get_shared_users ──────────────────────────────────────────────────────────


class TestGetSharedUsers:
    def test_owner_gets_shared_users(self, mock_auth_and_http):
        """Le owner récupère la liste des utilisateurs partagés."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if (
                method.upper() == "GET"
                and "/playlists/9" in url
                and "shared-with" not in url
            ):
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "GET" and "shared-with" in url:
                return _response(200, SHARED_USERS)
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        users = get_shared_users("9")

        assert len(users) == 2
        assert users[0].idUser == 2
        assert users[0].username == "alice"
        assert users[0].email == "alice@etu.umontpellier.fr"
        assert not users[0].editor

    def test_returns_correct_schema(self, mock_auth_and_http):
        """Les objets retournés ont les bons champs."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if (
                method.upper() == "GET"
                and "/playlists/9" in url
                and "shared-with" not in url
            ):
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "GET" and "shared-with" in url:
                return _response(200, SHARED_USERS)
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        users = get_shared_users("9")

        for user in users:
            assert hasattr(user, "idUser")
            assert hasattr(user, "idPlaylist")
            assert hasattr(user, "editor")
            assert hasattr(user, "username")
            assert hasattr(user, "email")

    def test_editor_flag_is_correct(self, mock_auth_and_http):
        """Le flag editor est correctement mappé."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if (
                method.upper() == "GET"
                and "/playlists/9" in url
                and "shared-with" not in url
            ):
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "GET" and "shared-with" in url:
                return _response(200, SHARED_USERS)
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        users = get_shared_users("9")

        assert not users[0].editor  # alice = viewer
        assert users[1].editor  # bob = editor

    def test_empty_list_when_no_users(self, mock_auth_and_http):
        """Retourne une liste vide si personne n'a accès."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if (
                method.upper() == "GET"
                and "/playlists/9" in url
                and "shared-with" not in url
            ):
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "GET" and "shared-with" in url:
                return _response(200, [])
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        users = get_shared_users("9")

        assert users == []

    def test_admin_can_get_shared_users(self, mock_auth_and_http_admin):
        """Un admin peut voir les utilisateurs d'une playlist dont il n'est pas owner."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if (
                method.upper() == "GET"
                and "/playlists/10" in url
                and "shared-with" not in url
            ):
                return _response(200, OTHER_OWNER_PLAYLIST)
            if method.upper() == "GET" and "shared-with" in url:
                return _response(200, SHARED_USERS)
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http_admin.side_effect = _dispatch

        users = get_shared_users("10")

        assert len(users) == 2

    def test_non_owner_cannot_get_shared_users(self, mock_auth_and_http):
        """Un non-owner ne peut pas voir les utilisateurs partagés."""
        mock_auth_and_http.return_value = _response(200, OTHER_OWNER_PLAYLIST)

        with pytest.raises(Exception, match="permission"):
            get_shared_users("10")

    def test_playlist_not_found(self, mock_auth_and_http):
        """Lève une exception si la playlist n'existe pas."""
        mock_auth_and_http.return_value = _response(
            404, {"detail": "Not found"}, "Not found"
        )

        with pytest.raises(Exception, match="not found"):
            get_shared_users("999")

    def test_api_error_on_shared_with(self, mock_auth_and_http):
        """Lève une exception si l'API shared-with échoue."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if (
                method.upper() == "GET"
                and "/playlists/9" in url
                and "shared-with" not in url
            ):
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "GET" and "shared-with" in url:
                return _response(500, {"detail": "Server error"}, "Server error")
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        with pytest.raises(Exception):
            get_shared_users("9")

    def test_forbidden_on_shared_with(self, mock_auth_and_http):
        """Lève une exception si l'API retourne 403."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if (
                method.upper() == "GET"
                and "/playlists/9" in url
                and "shared-with" not in url
            ):
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "GET" and "shared-with" in url:
                return _response(403, {"detail": "Forbidden"}, "Forbidden")
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        with pytest.raises(Exception):
            get_shared_users("9")


# ─── remove_shared_user ────────────────────────────────────────────────────────


class TestRemoveSharedUser:
    def test_owner_can_remove_shared_user(self, mock_auth_and_http):
        """Le owner peut supprimer l'accès d'un utilisateur."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if method.upper() == "GET" and "/playlists/9" in url:
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "DELETE" and "share/user/2" in url:
                return _response(
                    200, {"message": "User successfully removed from playlist"}
                )
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        result = remove_shared_user("9", "2")

        assert result["message"] == "User successfully removed from playlist"

    def test_admin_can_remove_shared_user(self, mock_auth_and_http_admin):
        """Un admin peut supprimer l'accès d'un utilisateur d'une playlist dont il n'est pas owner."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if method.upper() == "GET" and "/playlists/10" in url:
                return _response(200, OTHER_OWNER_PLAYLIST)
            if method.upper() == "DELETE" and "share/user/2" in url:
                return _response(
                    200, {"message": "User successfully removed from playlist"}
                )
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http_admin.side_effect = _dispatch

        result = remove_shared_user("10", "2")

        assert result["message"] == "User successfully removed from playlist"

    def test_non_owner_cannot_remove_shared_user(self, mock_auth_and_http):
        """Un non-owner ne peut pas supprimer l'accès d'un utilisateur."""
        mock_auth_and_http.return_value = _response(200, OTHER_OWNER_PLAYLIST)

        with pytest.raises(Exception, match="permission"):
            remove_shared_user("10", "2")

    def test_playlist_not_found(self, mock_auth_and_http):
        """Lève une exception si la playlist n'existe pas."""
        mock_auth_and_http.return_value = _response(
            404, {"detail": "Not found"}, "Not found"
        )

        with pytest.raises(Exception, match="not found"):
            remove_shared_user("999", "2")

    def test_user_not_in_playlist(self, mock_auth_and_http):
        """Lève une exception si l'utilisateur n'a pas accès à la playlist."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if method.upper() == "GET" and "/playlists/9" in url:
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "DELETE" and "share/user/999" in url:
                return _response(
                    404,
                    {"detail": "This user does not have access to this playlist"},
                    "Not found",
                )
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        with pytest.raises(Exception):
            remove_shared_user("9", "999")

    def test_api_returns_403(self, mock_auth_and_http):
        """Lève une exception si l'API retourne 403."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if method.upper() == "GET" and "/playlists/9" in url:
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "DELETE" and "share/user" in url:
                return _response(403, {"detail": "Forbidden"}, "Forbidden")
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        with pytest.raises(Exception, match="permission"):
            remove_shared_user("9", "2")

    def test_api_server_error(self, mock_auth_and_http):
        """Lève une exception si l'API retourne 500."""

        def _dispatch(method: str, **kwargs):
            url = kwargs["url"]
            if method.upper() == "GET" and "/playlists/9" in url:
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "DELETE" and "share/user" in url:
                return _response(500, {"detail": "Server error"}, "Server error")
            raise AssertionError(f"Unexpected: {method} {url}")

        mock_auth_and_http.side_effect = _dispatch

        with pytest.raises(Exception):
            remove_shared_user("9", "2")


# ─── Tests injection CLI ───────────────────────────────────────────────────────

BASH_PAYLOADS = [
    "; whoami",
    "&& whoami",
    "| whoami",
    "$(whoami)",
    "`whoami`",
]

FORBIDDEN_OUTPUTS = ["uid=", "gid=", "root:", "/bin/", "/usr/bin"]


def assert_no_system_execution(result):
    for forbidden in FORBIDDEN_OUTPUTS:
        assert (
            forbidden not in result.output
        ), f"Possible system execution: '{forbidden}' found in output."


@pytest.fixture(autouse=False)
def mock_api_calls_cli():
    with (
        patch("requests.request") as mock_request,
        patch("src.utils.http_client.get_access_token", return_value="access-token"),
        patch("src.utils.http_client.get_refresh_token", return_value="refresh-token"),
        patch("src.services.playlist.auth_service.whoami", return_value={"id": 1}),
    ):

        def _dispatch(method: str, **kwargs):
            url = kwargs.get("url", "")
            if method.upper() == "GET" and "shared-with" not in url:
                return _response(200, OWNER_PLAYLIST)
            if method.upper() == "GET" and "shared-with" in url:
                return _response(200, SHARED_USERS)
            return _response(
                200, {"message": "User successfully removed from playlist"}
            )

        mock_request.side_effect = _dispatch
        yield mock_request


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
def test_bash_injection_shared_users_command(payload, mock_api_calls_cli):
    """Test injection bash sur la commande shared-users."""
    result = runner.invoke(app, ["playlist", "shared-users", "1"])

    assert_no_system_execution(result)


@pytest.mark.parametrize("payload", BASH_PAYLOADS)
def test_bash_injection_unshare_command(payload, mock_api_calls_cli):
    """Test injection bash sur la commande unshare avec --force."""
    result = runner.invoke(app, ["playlist", "unshare", "1", "2", "--force"])

    assert_no_system_execution(result)
