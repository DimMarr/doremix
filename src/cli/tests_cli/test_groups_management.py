from __future__ import annotations

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app
from src.models.group import GroupMemberSchema, GroupSchema, GroupWithUsersSchema
from src.services.admin_group import (
    add_user_to_group,
    create_group,
    delete_group,
    get_all_groups,
    get_user_display_name,
)
from src.utils.exceptions import (
    GroupExistsError,
    GroupMembershipError,
    UserNotFoundError,
)


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
    ):
        yield mock_request


# ─── service layer ────────────────────────────────────────────────────────────


def test_get_all_groups_success(mock_auth_and_http):
    payload = [
        {
            "idGroup": 1,
            "groupName": "Team A",
            "users": [
                {
                    "idUser": 2,
                    "username": "sarah",
                    "email": "sarah@etu.umontpellier.fr",
                }
            ],
        }
    ]
    mock_auth_and_http.return_value = _response(200, payload)

    groups = get_all_groups()

    assert len(groups) == 1
    assert groups[0].idGroup == 1
    assert groups[0].groupName == "Team A"
    assert groups[0].users[0].username == "sarah"


def test_create_group_conflict(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(
        409,
        {"detail": "Group with this name already exists"},
        text="Conflict",
    )

    with pytest.raises(GroupExistsError):
        create_group("Team A")


def test_create_group_with_trailing_slash_fallback(mock_auth_and_http):
    mock_auth_and_http.side_effect = [
        _response(404, {"detail": "Not found"}, text="Not found"),
        _response(201, {"idGroup": 12, "groupName": "Fallback Team"}),
    ]

    group = create_group("Fallback Team")

    assert group.idGroup == 12
    assert group.groupName == "Fallback Team"


def test_add_user_to_group_user_not_found(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(
        404, {"detail": "User not found"}, text="Not found"
    )

    with pytest.raises(UserNotFoundError):
        add_user_to_group(1, 999)


def test_add_user_to_group_already_member(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(
        409, {"detail": "User is already in this group"}, text="Conflict"
    )

    with pytest.raises(GroupMembershipError):
        add_user_to_group(1, 2)


def test_delete_group_accepts_204(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(204, None)

    delete_group(1)


def test_get_user_display_name_success(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(
        200,
        {
            "idUser": 2,
            "username": "sarah",
            "email": "sarah@etu.umontpellier.fr",
        },
    )

    label = get_user_display_name(2)

    assert label == "sarah (sarah@etu.umontpellier.fr)"


# ─── CLI layer ────────────────────────────────────────────────────────────────


@pytest.fixture()
def mock_admin_role():
    with patch("src.commands.admin.get_user", return_value={"role": "ADMIN"}):
        yield


def test_cli_group_add_user_shows_user_name(mock_admin_role):
    with (
        patch(
            "src.commands.admin.get_user_display_name",
            return_value="sarah (sarah@etu.umontpellier.fr)",
        ),
        patch("src.commands.admin.add_user_to_group", return_value=None),
    ):
        result = runner.invoke(app, ["group", "add-user", "1", "2"])

    assert result.exit_code == 0
    assert "sarah (sarah@etu.umontpellier.fr) added to group 1" in result.output


def test_cli_group_add_user_already_member_has_precise_message(mock_admin_role):
    with (
        patch(
            "src.commands.admin.get_user_display_name",
            return_value="sarah (sarah@etu.umontpellier.fr)",
        ),
        patch(
            "src.commands.admin.add_user_to_group",
            side_effect=GroupMembershipError("already in group"),
        ),
    ):
        result = runner.invoke(app, ["group", "add-user", "1", "2"])

    assert result.exit_code == 0
    assert "sarah (sarah@etu.umontpellier.fr) is already in group 1" in result.output


def test_cli_group_add_user_unknown_user(mock_admin_role):
    with patch(
        "src.commands.admin.get_user_display_name",
        side_effect=UserNotFoundError("User 99 not found"),
    ):
        result = runner.invoke(app, ["group", "add-user", "1", "99"])

    assert result.exit_code == 0
    assert "User 99 not found" in result.output


def test_cli_group_create_duplicate_name(mock_admin_role):
    existing_group = GroupWithUsersSchema(
        idGroup=1,
        groupName="Team A",
        users=[],
    )

    with patch("src.commands.admin.get_all_groups", return_value=[existing_group]):
        result = runner.invoke(app, ["group", "create", "--name", "team a"])

    assert result.exit_code == 0
    assert "A group with this name already exists" in result.output


def test_cli_group_list_renders_members_table(mock_admin_role):
    payload = [
        GroupWithUsersSchema(
            idGroup=1,
            groupName="Team A",
            users=[
                GroupMemberSchema(
                    idUser=2,
                    username="sarah",
                    email="sarah@etu.umontpellier.fr",
                )
            ],
        )
    ]

    with patch("src.commands.admin.get_all_groups", return_value=payload):
        result = runner.invoke(app, ["group", "list"])

    assert result.exit_code == 0
    assert "Group #1 - Team A" in result.output
    assert "sarah" in result.output


def test_cli_group_delete_force_success(mock_admin_role):
    with patch("src.commands.admin.delete_group", return_value=None):
        result = runner.invoke(app, ["group", "delete", "1", "--force"])

    assert result.exit_code == 0
    assert "Group 1 deleted successfully" in result.output
