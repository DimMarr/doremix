import pytest
from sqlalchemy.orm import Session
from models import User, Genre
from models.playlist import Playlist
from models.enums import PlaylistVisibility
from models.user_playlists import UserPlaylist


# ─── Fixtures locales ──────────────────────────────────────────────────────────


@pytest.fixture
def other_user(db: Session):
    user = User(
        username="alice",
        email="alice@etu.umontpellier.fr",
        password="hashed",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db: Session):
    user = User(
        username="admin",
        email="admin@etu.umontpellier.fr",
        password="hashed",
        idRole=3,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def third_user(db: Session):
    """Utilisateur sans aucun lien avec la playlist."""
    user = User(
        username="stranger",
        email="stranger@etu.umontpellier.fr",
        password="hashed",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def shared_playlist(db: Session, sample_user, sample_genre, other_user):
    """Playlist privée partagée avec other_user (viewer)."""
    playlist = Playlist(
        name="Shared Playlist",
        idOwner=sample_user.idUser,
        idGenre=sample_genre.idGenre,
        visibility=PlaylistVisibility.PRIVATE,
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)

    link = UserPlaylist(
        idUser=other_user.idUser,
        idPlaylist=playlist.idPlaylist,
        editor=False,
    )
    db.add(link)
    db.commit()
    return playlist


@pytest.fixture
def shared_playlist_with_editor(db: Session, sample_user, sample_genre, other_user):
    """Playlist privée partagée avec other_user (editor)."""
    playlist = Playlist(
        name="Editor Playlist",
        idOwner=sample_user.idUser,
        idGenre=sample_genre.idGenre,
        visibility=PlaylistVisibility.PRIVATE,
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)

    link = UserPlaylist(
        idUser=other_user.idUser,
        idPlaylist=playlist.idPlaylist,
        editor=True,
    )
    db.add(link)
    db.commit()
    return playlist


# ─── GET /playlists/{id}/shared-with ──────────────────────────────────────────


class TestSharedWith:
    # Succès
    def test_owner_can_see_shared_users(self, client, shared_playlist, other_user):
        """Le owner voit la liste des utilisateurs partagés."""
        response = client.get(f"/playlists/{shared_playlist.idPlaylist}/shared-with")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["idUser"] == other_user.idUser

    def test_returns_correct_schema(self, client, shared_playlist, other_user):
        """Le schéma retourné contient tous les champs attendus."""
        response = client.get(f"/playlists/{shared_playlist.idPlaylist}/shared-with")

        assert response.status_code == 200
        user = response.json()[0]
        assert "idUser" in user
        assert "idPlaylist" in user
        assert "editor" in user
        assert "username" in user
        assert "email" in user

    def test_returns_correct_values(self, client, shared_playlist, other_user):
        """Les valeurs retournées correspondent à l'utilisateur partagé."""
        response = client.get(f"/playlists/{shared_playlist.idPlaylist}/shared-with")

        assert response.status_code == 200
        user = response.json()[0]
        assert user["idUser"] == other_user.idUser
        assert user["username"] == other_user.username
        assert user["email"] == other_user.email
        assert not user["editor"]

    def test_viewer_flag_is_false(self, client, shared_playlist, other_user):
        """Un viewer a editor=False."""
        response = client.get(f"/playlists/{shared_playlist.idPlaylist}/shared-with")

        assert response.status_code == 200
        assert not response.json()[0]["editor"]

    def test_editor_flag_is_true(self, client, shared_playlist_with_editor, other_user):
        """Un editor a editor=True."""
        response = client.get(
            f"/playlists/{shared_playlist_with_editor.idPlaylist}/shared-with"
        )

        assert response.status_code == 200
        assert response.json()[0]["editor"]

    def test_empty_when_no_users(self, client, sample_playlist):
        """Retourne une liste vide si personne n'a accès."""
        response = client.get(f"/playlists/{sample_playlist.idPlaylist}/shared-with")

        assert response.status_code == 200
        assert response.json() == []

    def test_multiple_shared_users(
        self, client, db: Session, shared_playlist, third_user
    ):
        """Retourne tous les utilisateurs partagés."""
        link = UserPlaylist(
            idUser=third_user.idUser,
            idPlaylist=shared_playlist.idPlaylist,
            editor=False,
        )
        db.add(link)
        db.commit()

        response = client.get(f"/playlists/{shared_playlist.idPlaylist}/shared-with")

        assert response.status_code == 200
        assert len(response.json()) == 2

    # Droits
    def test_shared_user_can_see_shared_users(
        self, client_as_other_user, shared_playlist, other_user
    ):
        """Un utilisateur partagé peut voir la liste."""
        response = client_as_other_user.get(
            f"/playlists/{shared_playlist.idPlaylist}/shared-with"
        )

        assert response.status_code == 200

    def test_admin_can_see_shared_users(
        self, client_as_admin, shared_playlist, other_user
    ):
        """Un admin peut voir la liste même sans être owner."""
        response = client_as_admin.get(
            f"/playlists/{shared_playlist.idPlaylist}/shared-with"
        )

        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_stranger_cannot_see_shared_users(
        self, client_as_other_user, db: Session, sample_user, sample_genre
    ):
        """Un utilisateur sans lien avec la playlist ne peut pas voir la liste."""
        private_playlist = Playlist(
            name="Private",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PRIVATE,
        )
        db.add(private_playlist)
        db.commit()
        db.refresh(private_playlist)

        response = client_as_other_user.get(
            f"/playlists/{private_playlist.idPlaylist}/shared-with"
        )

        assert response.status_code == 403

    # Cas limites
    def test_playlist_not_found(self, client):
        """Retourne 403 ou 404 si la playlist n'existe pas."""
        response = client.get("/playlists/999/shared-with")

        assert response.status_code in [403, 404]

    def test_invalid_playlist_id(self, client):
        """Retourne 422 si l'ID est invalide."""
        response = client.get("/playlists/invalid/shared-with")

        assert response.status_code == 422


# ─── DELETE /playlists/{id}/share/user/{user_id} ──────────────────────────────


class TestUnshareUser:
    # Succès
    def test_owner_can_remove_shared_user(
        self, client, db: Session, shared_playlist, other_user
    ):
        """Le owner peut supprimer l'accès d'un viewer."""
        response = client.delete(
            f"/playlists/{shared_playlist.idPlaylist}/share/user/{other_user.idUser}"
        )

        assert response.status_code == 200
        assert response.json()["message"] == "User successfully removed from playlist"

    def test_link_is_deleted_in_db(
        self, client, db: Session, shared_playlist, other_user
    ):
        """Le lien est bien supprimé en base après la suppression."""
        client.delete(
            f"/playlists/{shared_playlist.idPlaylist}/share/user/{other_user.idUser}"
        )

        link = (
            db.query(UserPlaylist)
            .filter(
                UserPlaylist.idPlaylist == shared_playlist.idPlaylist,
                UserPlaylist.idUser == other_user.idUser,
            )
            .first()
        )
        assert link is None

    def test_owner_can_remove_editor(
        self, client, db: Session, shared_playlist_with_editor, other_user
    ):
        """Le owner peut aussi supprimer un editor."""
        response = client.delete(
            f"/playlists/{shared_playlist_with_editor.idPlaylist}/share/user/{other_user.idUser}"
        )

        assert response.status_code == 200

    def test_other_shared_users_unaffected(
        self, client, db: Session, shared_playlist, other_user, third_user
    ):
        """Supprimer un utilisateur ne supprime pas les autres."""
        link = UserPlaylist(
            idUser=third_user.idUser,
            idPlaylist=shared_playlist.idPlaylist,
            editor=False,
        )
        db.add(link)
        db.commit()

        client.delete(
            f"/playlists/{shared_playlist.idPlaylist}/share/user/{other_user.idUser}"
        )

        remaining = (
            db.query(UserPlaylist)
            .filter(UserPlaylist.idPlaylist == shared_playlist.idPlaylist)
            .all()
        )
        assert len(remaining) == 1
        assert remaining[0].idUser == third_user.idUser

    # Droits
    def test_admin_can_remove_shared_user(
        self, client_as_admin, db: Session, shared_playlist, other_user
    ):
        """Un admin peut supprimer l'accès d'un utilisateur."""
        response = client_as_admin.delete(
            f"/playlists/{shared_playlist.idPlaylist}/share/user/{other_user.idUser}"
        )

        assert response.status_code == 200

    def test_non_owner_cannot_remove_shared_user(
        self, client_as_other_user, db: Session, sample_user, sample_genre, third_user
    ):
        """Un utilisateur non owner non admin ne peut pas supprimer un accès."""
        playlist = Playlist(
            name="Protected",
            idOwner=sample_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PRIVATE,
        )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

        link = UserPlaylist(
            idUser=third_user.idUser,
            idPlaylist=playlist.idPlaylist,
            editor=False,
        )
        db.add(link)
        db.commit()

        response = client_as_other_user.delete(
            f"/playlists/{playlist.idPlaylist}/share/user/{third_user.idUser}"
        )

        assert response.status_code == 403

    def test_shared_viewer_cannot_remove_user(
        self, client_as_other_user, shared_playlist, other_user, third_user, db: Session
    ):
        """Un viewer partagé ne peut pas supprimer un autre utilisateur."""
        link = UserPlaylist(
            idUser=third_user.idUser,
            idPlaylist=shared_playlist.idPlaylist,
            editor=False,
        )
        db.add(link)
        db.commit()

        response = client_as_other_user.delete(
            f"/playlists/{shared_playlist.idPlaylist}/share/user/{third_user.idUser}"
        )

        assert response.status_code == 403

    def test_shared_editor_cannot_remove_user(
        self, client_as_other_user, shared_playlist_with_editor, third_user, db: Session
    ):
        """Un editor partagé ne peut pas supprimer un autre utilisateur."""
        link = UserPlaylist(
            idUser=third_user.idUser,
            idPlaylist=shared_playlist_with_editor.idPlaylist,
            editor=False,
        )
        db.add(link)
        db.commit()

        response = client_as_other_user.delete(
            f"/playlists/{shared_playlist_with_editor.idPlaylist}/share/user/{third_user.idUser}"
        )

        assert response.status_code == 403

    # Cas limites
    def test_user_not_in_playlist(self, client, shared_playlist):
        """Retourne 404 si l'utilisateur n'a pas accès à la playlist."""
        response = client.delete(
            f"/playlists/{shared_playlist.idPlaylist}/share/user/999"
        )

        assert response.status_code == 404

    def test_playlist_not_found(self, client, other_user):
        """Retourne 404 si la playlist n'existe pas."""
        response = client.delete(f"/playlists/999/share/user/{other_user.idUser}")

        assert response.status_code == 404

    def test_idempotent_double_delete(self, client, shared_playlist, other_user):
        """Supprimer deux fois le même utilisateur retourne 404 la deuxième fois."""
        client.delete(
            f"/playlists/{shared_playlist.idPlaylist}/share/user/{other_user.idUser}"
        )
        response = client.delete(
            f"/playlists/{shared_playlist.idPlaylist}/share/user/{other_user.idUser}"
        )

        assert response.status_code == 404

    def test_invalid_user_id(self, client, shared_playlist):
        """Retourne 422 si l'ID utilisateur est invalide."""
        response = client.delete(
            f"/playlists/{shared_playlist.idPlaylist}/share/user/invalid"
        )

        assert response.status_code == 422

    def test_invalid_playlist_id(self, client, other_user):
        """Retourne 422 si l'ID playlist est invalide."""
        response = client.delete(f"/playlists/invalid/share/user/{other_user.idUser}")

        assert response.status_code == 422
