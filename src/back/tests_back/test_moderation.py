from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import middleware.auth_middleware as auth_middleware
from database import get_db
from middleware.auth_middleware import get_current_user_id
from models.access_token import AccessToken
from models.refresh_token import RefreshToken
from models.user import User
from routes.moderation import router as moderation_router
from routes.users import router as users_router


def create_user(
    db: Session,
    email: str,
    username: str,
    id_role: int,
    banned: bool = False,
) -> User:
    user = User(
        email=email,
        username=username,
        password="hashed-password",
        idRole=id_role,
        banned=banned,
        isVerified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_actor(client: TestClient, monkeypatch: pytest.MonkeyPatch, actor: User):
    client.app.dependency_overrides[get_current_user_id] = lambda: actor.idUser
    monkeypatch.setattr(
        auth_middleware, "get_current_user", lambda request, _actor=actor: _actor
    )


@pytest.fixture(scope="function")
def moderation_client(db: Session):
    app = FastAPI()
    app.include_router(moderation_router)
    app.include_router(users_router)

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_get_ban_candidates_filters_self_admin_and_banned(
    moderation_client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
):
    actor = create_user(db, "mod@etu.umontpellier.fr", "mod_actor", 2)
    candidate_user = create_user(db, "user1@etu.umontpellier.fr", "candidate_user", 1)
    candidate_moderator = create_user(
        db, "mod2@etu.umontpellier.fr", "candidate_mod", 2
    )
    admin = create_user(db, "admin@umontpellier.fr", "admin_user", 3)
    banned_user = create_user(
        db, "banned@etu.umontpellier.fr", "already_banned", 1, banned=True
    )

    set_actor(moderation_client, monkeypatch, actor)
    response = moderation_client.get("/moderation/ban-candidates")

    assert response.status_code == 200
    response_ids = {item["idUser"] for item in response.json()}
    assert candidate_user.idUser in response_ids
    assert candidate_moderator.idUser in response_ids
    assert actor.idUser not in response_ids
    assert admin.idUser not in response_ids
    assert banned_user.idUser not in response_ids


def test_ban_user_sets_banned_and_revokes_all_tokens(
    moderation_client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
):
    actor = create_user(db, "mod@etu.umontpellier.fr", "mod_actor", 2)
    target = create_user(db, "target@etu.umontpellier.fr", "target_user", 1)

    access_token = AccessToken(
        token="access-token-for-target",
        idUser=target.idUser,
        expiresAt=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    refresh_token = RefreshToken(
        token="refresh-token-for-target",
        idUser=target.idUser,
        expiresAt=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(access_token)
    db.add(refresh_token)
    db.commit()

    set_actor(moderation_client, monkeypatch, actor)
    response = moderation_client.post(f"/moderation/users/{target.idUser}/ban")

    assert response.status_code == 200
    payload = response.json()
    assert payload["idUser"] == target.idUser
    assert payload["banned"] is True

    db.refresh(target)
    assert target.banned is True
    assert (
        db.query(AccessToken).filter(AccessToken.idUser == target.idUser).count() == 0
    )
    assert (
        db.query(RefreshToken).filter(RefreshToken.idUser == target.idUser).count() == 0
    )


def test_moderator_cannot_ban_admin(
    moderation_client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
):
    actor = create_user(db, "mod@etu.umontpellier.fr", "mod_actor", 2)
    admin = create_user(db, "admin@umontpellier.fr", "admin_user", 3)

    set_actor(moderation_client, monkeypatch, actor)
    response = moderation_client.post(f"/moderation/users/{admin.idUser}/ban")

    assert response.status_code == 403
    assert response.json()["detail"] == "Moderators cannot ban admin users"


def test_admin_cannot_access_moderation_endpoints(
    moderation_client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
):
    admin = create_user(db, "admin@umontpellier.fr", "admin_user", 3)

    set_actor(moderation_client, monkeypatch, admin)
    response = moderation_client.get("/moderation/ban-candidates")

    assert response.status_code == 403
    assert response.json()["detail"] == "Required role: MODERATOR"


def test_users_listing_is_admin_only(
    moderation_client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
):
    moderator = create_user(db, "mod@etu.umontpellier.fr", "mod_actor", 2)
    admin = create_user(db, "admin@umontpellier.fr", "admin_user", 3)

    set_actor(moderation_client, monkeypatch, moderator)
    response = moderation_client.get("/users/")
    assert response.status_code == 403

    set_actor(moderation_client, monkeypatch, admin)
    response = moderation_client.get("/users/")
    assert response.status_code == 200
