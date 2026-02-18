import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from fastapi.testclient import TestClient
from database import Base, get_db
from routes.playlists import router as playlists_router
from routes.users import router as users_router
from routes.search_router import router as search_router
from models import User, Genre
from models.enums import PlaylistVisibility
from models.playlist import Playlist

# Crée une base de données SQLite en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Crée l'application FastAPI
app = FastAPI()
app.include_router(playlists_router)
app.include_router(users_router)
app.include_router(search_router)


@pytest.fixture(scope="function")
def db():
    """Crée une base de données pour chaque test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db, sample_user):
    """Crée un client de test avec dépendance override et utilisateur simulé."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_current_user_id():
        return sample_user.idUser

    app.dependency_overrides[get_db] = override_get_db
    # Override auth dependencies so routes depending on user or user id work in tests
    from middleware.auth_middleware import get_current_user_id, get_current_user

    app.dependency_overrides[get_current_user_id] = (
        lambda: override_get_current_user_id()
    )
    app.dependency_overrides[get_current_user] = lambda: sample_user

    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_user(db: Session):
    """Crée un utilisateur de test"""
    user = User(
        username="sarah",
        email="sarah@etu.umontpellier.fr",
        password="$2b$12$MfGljJQRrXEFoIXXniPzFueRzeO.wSwElO8U1uRqmq.f15VHw7kIK",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def sample_genre(db: Session):
    """Crée un genre de test"""
    genre = Genre(label="Rock")
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


@pytest.fixture
def sample_playlist(db, sample_user, sample_genre):
    """Crée une playlist de test"""
    playlist = Playlist(
        name="Test Playlist",
        idOwner=sample_user.idUser,
        idGenre=sample_genre.idGenre,
        visibility=PlaylistVisibility.PUBLIC,
    )
    db.add(playlist)
    db.commit()
    db.refresh(playlist)
    return playlist


@pytest.fixture
def sample_playlists(db: Session, sample_user, sample_genre):
    """Crée plusieurs playlists de test."""
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
    db.commit()

    for playlist in playlists:
        db.refresh(playlist)

    return playlists
