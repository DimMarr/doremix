import os

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from database import Base, get_db
from routes.playlists import router as playlists_router
from routes.users import router as users_router
from routes.search_router import router as search_router
from models import User, Genre
from models.enums import PlaylistVisibility
from models.playlist import Playlist
from middleware.auth_middleware import get_current_user_id, get_current_user


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

app = FastAPI()
app.include_router(playlists_router)
app.include_router(users_router)
app.include_router(search_router)


@pytest_asyncio.fixture(scope="function")
async def db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def sample_user(db: AsyncSession):
    """Crée un utilisateur de test"""
    user = User(
        username="sarah",
        email="sarah@etu.umontpellier.fr",
        password="$2b$12$MfGljJQRrXEFoIXXniPzFueRzeO.wSwElO8U1uRqmq.f15VHw7kIK",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def other_user(db: AsyncSession):
    """Crée un second utilisateur (ni owner ni admin)."""
    user = User(
        username="alice",
        email="alice@etu.umontpellier.fr",
        password="hashed",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def admin_user(db: AsyncSession):
    """Crée un utilisateur admin."""
    user = User(
        username="admin",
        email="admin@etu.umontpellier.fr",
        password="hashed",
        idRole=3,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def sample_genre(db: AsyncSession):
    """Crée un genre de test"""
    genre = Genre(label="Rock")
    db.add(genre)
    await db.commit()
    await db.refresh(genre)
    return genre


@pytest_asyncio.fixture
async def sample_playlist(db: AsyncSession, sample_user, sample_genre):
    playlist = Playlist(
        name="Test Playlist",
        idOwner=sample_user.idUser,
        idGenre=sample_genre.idGenre,
        visibility=PlaylistVisibility.PUBLIC,
    )
    db.add(playlist)
    await db.commit()
    await db.refresh(playlist)
    return playlist


@pytest_asyncio.fixture
async def sample_playlists(db: AsyncSession, sample_user, sample_genre):
    playlists = [
        Playlist(
            name="My Favorite Songs",
            idGenre=sample_genre.idGenre,
            idOwner=sample_user.idUser,
            vote=10,
            visibility=PlaylistVisibility.PUBLIC,
        ),
        Playlist(
            name="Private Mix",
            idGenre=sample_genre.idGenre,
            idOwner=sample_user.idUser,
            vote=5,
            visibility=PlaylistVisibility.PRIVATE,
        ),
    ]
    db.add_all(playlists)
    await db.commit()
    for playlist in playlists:
        await db.refresh(playlist)
    return playlists


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession, sample_user):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = lambda: sample_user.idUser
    app.dependency_overrides[get_current_user] = lambda: sample_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client_as_other_user(db: AsyncSession, other_user):
    """Client authentifié en tant qu'utilisateur non owner non admin."""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = lambda: other_user.idUser
    app.dependency_overrides[get_current_user] = lambda: other_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client_as_admin(db: AsyncSession, admin_user):
    """Client authentifié en tant qu'admin."""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_id] = lambda: admin_user.idUser
    app.dependency_overrides[get_current_user] = lambda: admin_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
