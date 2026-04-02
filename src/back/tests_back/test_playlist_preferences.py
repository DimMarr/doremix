# src/back/tests_back/test_playlist_preferences.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_playlist_preferences import UserPlaylistPreferences


class TestGetPlaylistPreferences:
    @pytest.mark.asyncio
    async def test_get_preferences_default_when_none_exist(self, client):
        """Returns date_desc defaults when no row exists for the user."""
        response = await client.get("/playlists/preferences")
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "date_desc"
        assert data["custom_order"] is None

    @pytest.mark.asyncio
    async def test_get_preferences_returns_saved_row(self, client, db: AsyncSession, sample_user):
        """Returns the stored sort_mode when a row already exists."""
        prefs = UserPlaylistPreferences(
            idUser=sample_user.idUser,
            sort_mode="name_asc",
            custom_order=None,
        )
        db.add(prefs)
        await db.commit()

        response = await client.get("/playlists/preferences")
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "name_asc"

    @pytest.mark.asyncio
    async def test_get_preferences_returns_custom_order(self, client, db: AsyncSession, sample_user):
        """Returns the custom_order array when sort_mode is custom."""
        prefs = UserPlaylistPreferences(
            idUser=sample_user.idUser,
            sort_mode="custom",
            custom_order=[3, 1, 2],
        )
        db.add(prefs)
        await db.commit()

        response = await client.get("/playlists/preferences")
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "custom"
        assert data["custom_order"] == [3, 1, 2]


class TestUpdatePlaylistPreferences:
    @pytest.mark.asyncio
    async def test_put_creates_row_on_first_save(self, client, db: AsyncSession, sample_user):
        """Creates a new preferences row when none exists."""
        response = await client.put(
            "/playlists/preferences",
            json={"sort_mode": "name_asc", "custom_order": None},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "name_asc"
        assert data["custom_order"] is None

    @pytest.mark.asyncio
    async def test_put_updates_existing_row(self, client, db: AsyncSession, sample_user):
        """Overwrites an existing preferences row."""
        prefs = UserPlaylistPreferences(
            idUser=sample_user.idUser, sort_mode="date_desc", custom_order=None
        )
        db.add(prefs)
        await db.commit()

        response = await client.put(
            "/playlists/preferences",
            json={"sort_mode": "custom", "custom_order": [5, 3, 1]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sort_mode"] == "custom"
        assert data["custom_order"] == [5, 3, 1]

    @pytest.mark.asyncio
    async def test_put_rejects_invalid_sort_mode(self, client):
        """Returns 422 for an unrecognised sort_mode value."""
        response = await client.put(
            "/playlists/preferences",
            json={"sort_mode": "bogus", "custom_order": None},
        )
        assert response.status_code == 422
