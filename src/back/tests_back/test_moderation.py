import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from datetime import datetime, timedelta, timezone
import pytest_asyncio
from fastapi import FastAPI, Request
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from database import get_db
from models.access_token import AccessToken
from models.refresh_token import RefreshToken
from models.user import User
from routes.moderation import router as moderation_router
from routes.users import router as users_router


async def create_user(
    db: AsyncSession,
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
    await db.commit()
    await db.refresh(user)
    return user


def make_auth_middleware(actor: User):
    class FakeAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            request.state.user = actor
            request.state.user_id = actor.idUser
            return await call_next(request)

    return FakeAuthMiddleware


def build_client(db: AsyncSession, actor: User) -> AsyncClient:
    app = FastAPI()
    app.add_middleware(make_auth_middleware(actor))
    app.include_router(moderation_router)
    app.include_router(users_router)

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_get_ban_candidates_filters_self_admin_and_banned(db: AsyncSession):
    actor = await create_user(db, "mod@etu.umontpellier.fr", "mod_actor", 2)
    candidate_user = await create_user(
        db, "user1@etu.umontpellier.fr", "candidate_user", 1
    )
    candidate_moderator = await create_user(
        db, "mod2@etu.umontpellier.fr", "candidate_mod", 2
    )
    admin = await create_user(db, "admin@umontpellier.fr", "admin_user", 3)
    banned_user = await create_user(
        db, "banned@etu.umontpellier.fr", "already_banned", 1, banned=True
    )

    async with build_client(db, actor) as client:
        response = await client.get("/moderation/ban-candidates")

    assert response.status_code == 200
    response_ids = {item["idUser"] for item in response.json()}
    assert candidate_user.idUser in response_ids
    assert candidate_moderator.idUser in response_ids
    assert actor.idUser not in response_ids
    assert admin.idUser not in response_ids
    assert banned_user.idUser not in response_ids


async def test_ban_user_sets_banned_and_revokes_all_tokens(db: AsyncSession):
    actor = await create_user(db, "mod@etu.umontpellier.fr", "mod_actor", 2)
    target = await create_user(db, "target@etu.umontpellier.fr", "target_user", 1)

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
    await db.commit()

    async with build_client(db, actor) as client:
        response = await client.post(f"/moderation/users/{target.idUser}/ban")

    assert response.status_code == 200
    payload = response.json()
    assert payload["idUser"] == target.idUser
    assert payload["banned"] is True

    await db.refresh(target)
    assert target.banned is True

    from sqlalchemy.future import select

    access_result = await db.execute(
        select(AccessToken).filter(AccessToken.idUser == target.idUser)
    )
    assert len(access_result.scalars().all()) == 0

    refresh_result = await db.execute(
        select(RefreshToken).filter(RefreshToken.idUser == target.idUser)
    )
    assert len(refresh_result.scalars().all()) == 0


async def test_moderator_cannot_ban_admin(db: AsyncSession):
    actor = await create_user(db, "mod@etu.umontpellier.fr", "mod_actor", 2)
    admin = await create_user(db, "admin@umontpellier.fr", "admin_user", 3)

    async with build_client(db, actor) as client:
        response = await client.post(f"/moderation/users/{admin.idUser}/ban")

    assert response.status_code == 403
    assert response.json()["detail"] == "You cannot ban an admin user"


async def test_admin_cannot_access_moderation_endpoints(db: AsyncSession):
    admin = await create_user(db, "admin@umontpellier.fr", "admin_user", 3)

    async with build_client(db, admin) as client:
        response = await client.get("/moderation/ban-candidates")

    assert response.status_code == 403
    assert response.json()["detail"] == "Required role: MODERATOR"


async def test_users_listing_is_admin_only(db: AsyncSession):
    moderator = await create_user(db, "mod@etu.umontpellier.fr", "mod_actor", 2)
    admin = await create_user(db, "admin@umontpellier.fr", "admin_user", 3)

    async with build_client(db, moderator) as client:
        response = await client.get("/users/")
    assert response.status_code == 403

    async with build_client(db, admin) as client:
        response = await client.get("/users/")
    assert response.status_code == 200
