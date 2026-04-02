from typing import Any
from src.utils.http_client import make_authenticated_request


def can_be_unbanned_list() -> Any:
    """Fetch the list of users that can be unbanned."""
    response = make_authenticated_request("GET", "/moderation/unban-candidates")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch unban candidates: {response.text}")
    return response.json()


def can_be_banned_list() -> Any:
    """Fetch the list of users that can be banned."""
    response = make_authenticated_request("GET", "/moderation/ban-candidates")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch ban candidates: {response.text}")
    return response.json()


def unban(user_id: int) -> Any:
    """Unban a user by their ID."""
    response = make_authenticated_request("POST", f"/moderation/users/{user_id}/unban")

    if response.status_code not in (200, 204):
        raise Exception(f"Failed to unban user {user_id}: {response.text}")
    return response.json() if response.text else {"status": "success"}


def ban(user_id: int) -> Any:
    """Ban a user by their ID."""
    response = make_authenticated_request("POST", f"/moderation/users/{user_id}/ban")
    if response.status_code not in (200, 204):
        raise Exception(f"Failed to ban user {user_id}: {response.text}")
    return response.json() if response.text else {"status": "success"}
