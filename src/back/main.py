import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from middleware.auth_middleware import AuthMiddleware
from middleware.rate_limiter import limiter, rate_limit_exceeded_handler
import uvicorn
from fastapi.staticfiles import StaticFiles
from scheduler import start_scheduler, scheduler


# Import routes
from routes import (
    authRouter,
    usersRouter,
    playlistsRouter,
    tracksRouter,
    artistsRouter,
    searchRouter,
    registerRouter,
    genresRouter,
    adminGenresRouter,
    moderationRouter,
    adminPlaylistsRouter,
)

routers = [
    authRouter,
    usersRouter,
    playlistsRouter,
    tracksRouter,
    artistsRouter,
    searchRouter,
    registerRouter,
    genresRouter,
    adminGenresRouter,
    moderationRouter,
    adminPlaylistsRouter,
]

pepper = os.getenv("PEPPER_KEY")
token_secret = os.getenv("TOKEN_SECRET_KEY")

if not pepper:
    raise ValueError("PEPPER_KEY is missing in .env file")
if not token_secret:
    raise ValueError("TOKEN_SECRET_KEY is missing in .env file")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                """
                UPDATE playlist
                SET vote = COALESCE(vote_totals.score, 0)
                FROM (
                    SELECT
                        playlist.idplaylist,
                        COALESCE(SUM(playlist_vote.value), 0) AS score
                    FROM playlist
                    LEFT JOIN playlist_vote
                        ON playlist_vote.idplaylist = playlist.idplaylist
                    GROUP BY playlist.idplaylist
                ) AS vote_totals
                WHERE vote_totals.idplaylist = playlist.idplaylist
                """
            )
        )
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan, redirect_slashes=False)

print("Setting up rate limiter with limit:", os.getenv("RATE_LIMIT", "100/minute"))
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

for router in routers:
    app.include_router(router)


# Create all tables
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                """
                UPDATE playlist
                SET vote = COALESCE(vote_totals.score, 0)
                FROM (
                    SELECT
                        playlist.idplaylist,
                        COALESCE(SUM(playlist_vote.value), 0) AS score
                    FROM playlist
                    LEFT JOIN playlist_vote
                        ON playlist_vote.idplaylist = playlist.idplaylist
                    GROUP BY playlist.idplaylist
                ) AS vote_totals
                WHERE vote_totals.idplaylist = playlist.idplaylist
                """
            )
        )


cors_origins = os.getenv("CORS_ORIGINS", "")

# On sépare les origines par des virgules et on enlève les espaces inutiles
allowed_origins = [origin.strip() for origin in cors_origins.split(",")]

print("Using following CORS origins:", allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add SlowAPI middleware for rate limiting
app.add_middleware(SlowAPIMiddleware)

app.middleware("http")(AuthMiddleware.verify_access_token)

app.mount("/covers", StaticFiles(directory="/app/uploads/covers"), name="covers")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
