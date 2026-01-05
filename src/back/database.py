from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")  # ex: postgresql+asyncpg://user:pass@db:5432/dbname

# Crée le moteur asynchrone
engine = create_async_engine(DATABASE_URL, echo=True)

# Crée une session asynchrone
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

# Dépendance FastAPI pour récupérer la session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
