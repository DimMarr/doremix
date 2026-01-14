import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import FastAPI
from fastapi.testclient import TestClient
from database import Base, get_db
from routes.playlists import router as playlists_router
from routes.users import router as users_router

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


@pytest.fixture(scope="function")
def db():
    """Crée une base de données pour chaque test."""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    """Crée un client de test avec dépendance override."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()
