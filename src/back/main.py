from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Import routes
from routes import (
    usersRouter,
    playlistsRouter,
    tracksRouter,
    artistsRouter,
    searchRouter,
    authRouter,
)

routers = [
    usersRouter,
    playlistsRouter,
    tracksRouter,
    artistsRouter,
    searchRouter,
    authRouter,
]

app = FastAPI()

# CORS configuration - MUST be added BEFORE including routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
for router in routers:
    app.include_router(router)

# Create all tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
