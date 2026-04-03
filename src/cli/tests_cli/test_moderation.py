from unittest.mock import MagicMock, patch
import pytest
import sys
from pathlib import Path
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.user import can_be_banned_list, ban, unban
from src.commands.user import app as user_app
from src.utils.exceptions import NotAuthenticatedError

runner = CliRunner()


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
        patch(
            "src.utils.http_client.auth_service.refresh",
            side_effect=NotAuthenticatedError("Session expired"),
        ),
    ):
        yield mock_request


def test_can_be_banned_list_success(mock_auth_and_http):
    payload = [
        {"idUser": 2, "username": "alice", "email": "alice@test.com", "banned": False}
    ]
    mock_auth_and_http.return_value = _response(200, payload)
    users = can_be_banned_list()
    assert len(users) == 1
    assert users[0]["username"] == "alice"


def test_can_be_banned_list_error(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(403, {}, "Forbidden")
    with pytest.raises(Exception, match="Failed to fetch ban candidates: Forbidden"):
        can_be_banned_list()


def test_ban_user_success(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, {"idUser": 2, "banned": True})
    result = ban(2)
    assert result.get("banned") is True


def test_unban_user_error(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(404, {}, "User not found")
    with pytest.raises(Exception, match="Failed to unban user 999"):
        unban(999)


def test_cli_ban_candidates(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(
        200,
        [{"idUser": 3, "username": "bob", "email": "bob@test.com", "banned": False}],
    )
    result = runner.invoke(user_app, ["ban-candidates"])
    assert result.exit_code == 0
    assert "bob" in result.output


def test_cli_unban_candidates_empty(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, [])
    result = runner.invoke(user_app, ["unban-candidates"])
    assert result.exit_code == 0
    assert "No users found" in result.output


def test_cli_ban_user(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, {"status": "success"})
    result = runner.invoke(user_app, ["ban", "2"])
    assert result.exit_code == 0
    assert "successfully banned" in result.output
