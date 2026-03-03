from unittest.mock import MagicMock, patch

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.exceptions import NotAuthenticatedError
from src.services.genre import (
    get_all,
    create,
    update,
    delete
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
        patch("src.utils.http_client.auth_service.refresh", side_effect=NotAuthenticatedError("Session expired")),
        patch("src.services.playlist.auth_service.whoami", return_value={"id": 1}),
    ):
        yield mock_request


def test_get_all_genres_success(mock_auth_and_http):
    payload = [
        {"idGenre": 1, "label": "Rock"},
        {"idGenre": 2, "label": "Jazz"},
    ]
    mock_auth_and_http.return_value = _response(200, payload)

    genres = get_all()
    assert len(genres) == 2
    assert genres[0].idGenre == 1
    assert genres[0].label == "Rock"
    assert genres[1].idGenre == 2
    assert genres[1].label == "Jazz"


def test_get_all_returns_empty_list(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, [])

    genres = get_all()
    assert genres == []


def test_get_all_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")

    with pytest.raises(Exception, match="Session expired"):
        get_all()


def test_get_all_raises_on_403(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(403, {}, text="Forbidden")

    with pytest.raises(Exception, match="Access denied"):
        get_all()



def test_create_genre_success(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(201, {"idGenre": 10, "label": "Metal"})

    genre = create(label="Metal")

    assert genre.idGenre == 10
    assert genre.label == "Metal"


def test_create_genre_raises_on_409_conflict(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(409, {}, text="Conflict")

    with pytest.raises(Exception, match="already exists"):
        create(label="Rock")


def test_create_genre_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")

    with pytest.raises(Exception, match="Session expired"):
        create(label="Blues")


def test_create_genre_raises_on_403(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(403, {}, text="Forbidden")

    with pytest.raises(Exception, match="Access denied"):
        create(label="Blues")



def test_update_genre_success(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, {"idGenre": 5, "label": "Classical"})

    genre = update(genre_id=5, label="Classical")

    assert genre.idGenre == 5
    assert genre.label == "Classical"


def test_update_genre_raises_on_404(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(404, {}, text="Not Found")

    with pytest.raises(Exception, match="not found"):
        update(genre_id=999, label="Ghost")


def test_update_genre_raises_on_409_conflict(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(409, {}, text="Conflict")

    with pytest.raises(Exception, match="already exists"):
        update(genre_id=3, label="Rock")


def test_update_genre_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")

    with pytest.raises(Exception, match="Session expired"):
        update(genre_id=1, label="New Label")


def test_update_genre_raises_on_403(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(403, {}, text="Forbidden")

    with pytest.raises(Exception, match="Access denied"):
        update(genre_id=1, label="New Label")


def test_delete_genre_success_on_200(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(200, {"message": "ok"})

    # Should not raise
    delete(genre_id=7)


def test_delete_genre_success_on_204(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(204, None)

    delete(genre_id=8)


def test_delete_genre_raises_on_400_linked_to_playlists(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(400, {}, text="Genre linked to playlists")

    with pytest.raises(Exception, match="linked"):
        delete(genre_id=3)


def test_delete_genre_raises_on_404(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(404, {}, text="Not Found")

    with pytest.raises(Exception, match="not found"):
        delete(genre_id=999)


def test_delete_genre_raises_on_401(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(401, {}, text="Unauthorized")

    with pytest.raises(Exception, match="Session expired"):
        delete(genre_id=1)


def test_delete_genre_raises_on_403(mock_auth_and_http):
    mock_auth_and_http.return_value = _response(403, {}, text="Forbidden")

    with pytest.raises(Exception, match="Access denied"):
        delete(genre_id=1)
