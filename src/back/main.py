from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# Import routes
from routes import usersRouter, playlistsRouter
routers = [usersRouter, playlistsRouter]

#from models import (Genre, Artist, User, Track, Playlist,TrackArtist, TrackPlaylist, UserPlaylist)

app = FastAPI()

for router in routers:
    app.include_router(router)

# Create all tables
Base.metadata.create_all(bind=engine)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def index():
    return {'message': 'API running'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
