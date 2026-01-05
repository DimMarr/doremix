from fastapi import FastAPI
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Import routes
from routes import usersRouter, playlistsRouter, tracksRouter
routers = [usersRouter, playlistsRouter, tracksRouter]

app = FastAPI()

for router in routers:
    app.include_router(router)

# Create all tables
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
app.on_event("startup")
async def on_startup():
    await init_models()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
