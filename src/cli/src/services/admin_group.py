from __future__ import annotations

from typing import Any

from src.models.group import GroupSchema, GroupWithUsersSchema
from src.utils.exceptions import (
    ApiRequestError,
    ForbiddenError,
    GroupExistsError,
    GroupMembershipError,
    GroupNotFoundError,
    NotAuthenticatedError,
    UserNotFoundError,
)
from src.utils.http_client import make_authenticated_request


def _detail(response: Any) -> str:
    try:
        payload = response.json()
    except ValueError:
        return str(response.text)
    if isinstance(payload, dict):
        return str(payload.get("detail", payload))
    return str(payload)


def _map_group_error(response: Any, context: str) -> None:
    detail = _detail(response)
    if response.status_code == 404:
        lowered = detail.lower()
        if "user not found" in lowered:
            raise UserNotFoundError(f"{context}: user not found")
        if "not in this group" in lowered:
            raise GroupMembershipError(detail)
        raise GroupNotFoundError(f"{context}: group not found")
    if response.status_code == 403:
        raise ForbiddenError(f"{context}: access denied (admin only)")
    if response.status_code == 401:
        raise NotAuthenticatedError(f"{context}: session expired, please login again")
    if response.status_code == 409:
        lowered = detail.lower()
        if "already exists" in lowered:
            raise GroupExistsError("A group with this name already exists")
        raise GroupMembershipError(detail)

    raise ApiRequestError(
        f"{context}: unexpected status {response.status_code} - {detail}"
    )


def _with_alt_slash(endpoint: str) -> str:
    if endpoint.endswith("/"):
        return endpoint[:-1]
    return f"{endpoint}/"


def _request_with_fallback(method: str, endpoint: str, **kwargs: Any) -> Any:
    response = make_authenticated_request(method, endpoint, **kwargs)

    if response.status_code == 404:
        detail = _detail(response).strip().lower()
        # Retry with/without trailing slash only for generic route-level 404.
        # Do not retry for resource-level 404 (e.g. "User not found").
        if detail in {"not found", "404: not found"}:
            alt_endpoint = _with_alt_slash(endpoint)
            response = make_authenticated_request(method, alt_endpoint, **kwargs)

    return response


def get_all_groups() -> list[GroupWithUsersSchema]:
    response = _request_with_fallback("GET", "/admin/groups/")
    if response.status_code not in (200,):
        _map_group_error(response, "Failed to fetch groups")
    return [GroupWithUsersSchema.model_validate(group) for group in response.json()]


def create_group(group_name: str) -> GroupSchema:
    response = _request_with_fallback(
        "POST", "/admin/groups/", json={"groupName": group_name}
    )
    if response.status_code not in (200, 201):
        _map_group_error(response, "Failed to create group")
    return GroupSchema.model_validate(response.json())


def delete_group(group_id: int) -> None:
    response = _request_with_fallback("DELETE", f"/admin/groups/{group_id}")
    if response.status_code not in (200, 204):
        _map_group_error(response, "Failed to delete group")


def add_user_to_group(group_id: int, user_id: int) -> None:
    response = _request_with_fallback(
        "POST", f"/admin/groups/{group_id}/users/{user_id}"
    )
    if response.status_code not in (200, 201):
        _map_group_error(response, "Failed to add user to group")


def remove_user_from_group(group_id: int, user_id: int) -> None:
    response = _request_with_fallback(
        "DELETE", f"/admin/groups/{group_id}/users/{user_id}"
    )
    if response.status_code not in (200, 204):
        _map_group_error(response, "Failed to remove user from group")


def get_user_display_name(user_id: int) -> str:
    response = _request_with_fallback("GET", f"/users/{user_id}")
    if response.status_code != 200:
        if response.status_code == 404:
            raise UserNotFoundError(f"User {user_id} not found")
        if response.status_code == 401:
            raise NotAuthenticatedError("Session expired, please login again")
        if response.status_code == 403:
            raise ForbiddenError("Access denied")
        raise ApiRequestError(f"Failed to fetch user {user_id}: {_detail(response)}")

    payload = response.json()
    username = payload.get("username") if isinstance(payload, dict) else None
    email = payload.get("email") if isinstance(payload, dict) else None

    if isinstance(username, str) and username.strip():
        if isinstance(email, str) and email.strip():
            return f"{username} ({email})"
        return username
    return f"User {user_id}"
