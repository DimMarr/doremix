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
    assert response.status_code != 500


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_playlist_by_user_injection(client, payload):
    response = client.get(f"/users/{payload}/playlists")
    assert response.status_code in [404, 400, 422]
    assert "detail" in response.json() or "error" in response.json()
    assert response.status_code != 500


# =================== PLAYLISTS ===================


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_playlist_create_injection(client, payload):
    response = client.post(
        "/playlists/",
        json={"name": payload, "description": "Test description", "user_id": 1},
    )
    assert response.status_code in (200, 400, 422)
    assert response.status_code != 500
    data = response.json()

    if response.status_code == 200:
        assert data["name"] == payload
    else:
        assert "detail" in data or "error" in data


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_playlists_id_injection(client, payload):
    response = client.get(f"/playlists/{payload}")
    assert response.status_code in [404, 400, 422]
    assert response.status_code != 500
    assert "detail" in response.json() or "error" in response.json()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_playlists_add_track_by_url_injection(client, payload):
    response = client.post(
        "/playlists/1/tracks/by-url",
        json={"url": "https://x.com?v=1" + payload, "title": "x"},
    )
    assert response.status_code in [404, 400, 422]
    assert response.status_code != 500
    assert "detail" in response.json() or "error" in response.json()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_upload_playlist_cover_injection(client, payload):
    files = {
        "file": (
            "../../evil.php.jpg",
            b"<?php echo 'pwned'; ?>",
            "image/jpeg",
        )
    }
    response = client.post(
        f"/playlists/{payload}/cover",
        files=files,
    )
    assert response.status_code in [404, 400, 422]
    assert response.status_code != 500
    assert "detail" in response.json() or "error" in response.json()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_cover_playlist_path_injection(client, payload):
    files = {
        "file": (
            "../../evil.php.jpg",
            b"<?php echo 'pwned'; ?>",
            "image/jpeg",
        )
    }
    response = client.post(
        f"/playlists/covers/{payload}",
        files=files,
    )
    assert response.status_code in [404, 405, 400, 422]
    assert response.status_code != 500
    assert "detail" in response.json() or "error" in response.json()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_remove_playlist_path_injection(client, payload):
    response = client.delete(f"/playlists/{payload}")
    assert response.status_code in [404, 400, 422]
    assert "detail" in response.json() or "error" in response.json()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_update_playlist_path_injection(client, payload):
    response = client.put(f"/playlists/{payload}")
    assert response.status_code in [404, 405, 400, 422]
    assert response.status_code != 500
    assert "detail" in response.json() or "error" in response.json()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_remove_track_from_playlist_path_injection(client, payload):
    response = client.delete(f"/playlists/1/tracks/{payload}")
    assert response.status_code in [404, 400, 422]
    assert response.status_code != 500
    assert "detail" in response.json() or "error" in response.json()


# =================== TRACKS ===================


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_add_track_by_url_injection(client, payload):
    response = client.post(
        "/playlists/2/tracks/by-url",
        json={"url": "https://x.com?v=1" + payload, "title": "Test Track"},
    )
    assert response.status_code in [404, 400, 422]
    assert response.status_code != 500
    assert "detail" in response.json() or "error" in response.json()


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_track_by_url_command_injection(client, payload):
    response = client.get(
        "/tracks/by-url",
        params={
            "url": "https://www.youtube.com/watch?v=hT8nvc6fxBs&list=RDCLAK5uy_mztvVkPbbOgYQFQUOi9VbLcZ4ewdmBczw&index=2"
            + payload
        },
    )
    assert response.status_code in (400, 422, 404)
    assert response.status_code != 500
    assert "detail" in response.json() or "error" in response.json()


# =================== ARTISTS ===================


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_artists_id_injection(client, payload):
    response = client.get(f"/artists/{payload}")
    assert response.status_code in [404, 400, 422]
    assert response.status_code != 500
    assert "detail" in response.json() or "error" in response.json()
