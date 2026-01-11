import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from middleware.rate_limiter import limiter, rate_limit_exceeded_handler

# Import routes
from routes import usersRouter, playlistsRouter, tracksRouter, artistsRouter

routers = [usersRouter, playlistsRouter, tracksRouter, artistsRouter]

app = FastAPI()

# Setup du rate limiter
print("Setting up rate limiter with limit:", os.getenv("RATE_LIMIT", "100/minute"))
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

for router in routers:
    app.include_router(router)

# Create all tables
Base.metadata.create_all(bind=engine)

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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
