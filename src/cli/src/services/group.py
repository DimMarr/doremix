from typing import Any
from src.utils.http_client import make_authenticated_request


def get_user_groups() -> Any:
    response = make_authenticated_request("GET", "/users/groups")
    if response.status_code != 200:
        raise Exception(f"Failed to fetch groups: {response.text}")
    return response.json()
