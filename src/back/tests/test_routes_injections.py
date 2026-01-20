import pytest

INJECTION_PAYLOADS = [
    "1 OR 1=1",
    "' OR '1'='1",
    "1; DROP TABLE users",
    "../etc/passwd",
    "../../etc/shadow",
    "$(whoami)",
    "`whoami`",
    "; whoami",
    "&& whoami",
    "| whoami",
    "<script>alert(1)</script>",
]

# =================== USERS ===================


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_users_id_injection(client, payload):
    response = client.get(f"/users/{payload}")
    assert response.status_code in [404, 400, 422]
    # 'detail' is present in error responses
    assert "detail" in response.json() or "error" in response.json()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_playlist_by_user_injection(client, payload):
    response = client.get(f"/users/{payload}/playlists")
    assert response.status_code in [404, 400, 422]
    assert "detail" in response.json() or "error" in response.json()


# =================== PLAYLISTS ===================


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_playlist_create_injection(client, payload):
    response = client.post(
        "/playlists/",
        json={"name": payload, "description": "Test description", "user_id": 1},
    )
    assert response.status_code in (200, 400, 422)
    if response.status_code == 200:
        data = response.json()
        # if created successfully, the name should match the payload
        assert data["name"] == payload


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_playlists_id_injection(client, payload):
    response = client.get(f"/playlists/{payload}")
    assert response.status_code in [404, 400, 422]
    assert "detail" in response.json() or "error" in response.json()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_playlist_add_tracks_path_injection(client, payload):
    response = client.get(f"/playlists/{payload}/track")
    assert response.status_code in [404, 405, 400, 422]
    assert "detail" in response.json() or "error" in response.json()


# TODO : upload cover


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_cover_playlist_path_injection(client, payload):
    response = client.post(
        f"/playlists/covers/{payload}",
        files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
    )
    assert response.status_code in [404, 405, 400, 422]


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_remove_playlist_path_injection(client, payload):
    response = client.delete(f"/playlists/{payload}")
    assert response.status_code in [404, 400, 422]


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_update_playlist_path_injection(client, payload):
    response = client.put(f"/playlists/{payload}")
    assert response.status_code in [404, 405, 400, 422]


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_remove_track_path_injection(client, payload):
    response = client.delete(f"/playlists/1/tracks/{payload}")
    assert response.status_code in [404, 400, 422]


# =================== TRACKS ===================


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_tracks_id_injection(client, payload):
    response = client.post(
        "/playlists/1/tracks/by-url",
        json={"url": "https://x.com?v=1" + payload, "title": "Test Track"},
    )
    assert response.status_code in [404, 400, 422]


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_track_by_url_command_injection(client, payload):
    res = client.get(
        "/tracks/by-url",
        params={
            "url": "https://www.youtube.com/watch?v=hT8nvc6fxBs&list=RDCLAK5uy_mztvVkPbbOgYQFQUOi9VbLcZ4ewdmBczw&index=2"
            + payload
        },
    )
    assert res.status_code in (400, 422, 404)


# =================== ARTISTS ===================


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_artists_id_injection(client, payload):
    response = client.get(f"/artists/{payload}")
    assert response.status_code in [404, 400, 422]
    assert "detail" in response.json() or "error" in response.json()
