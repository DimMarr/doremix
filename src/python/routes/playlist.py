from fastapi import APIRouter
from connect_db import connect_db
from ..models.visibility import Visibility
from ..models.playlist import PlaylistBase

router = APIRouter()

@router.get("")
def get_all_playlists(
    visibility: Visibility | None = None,
    search: str | None = None
):
    conn = connect_db()
    with conn.cursor() as curs:
        columns = ["id", "name", "owner_id", "track_count", "duration", "visibility", "created_at", "updated_at"]
        query = "SELECT * FROM playlist"
        params = []
        conditions = []

        if visibility:
            conditions.append("visibility=%s")
            params.append(visibility)
        if search:
            conditions.append("name ILIKE %s")
            params.append(f'%{search}%')
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        curs.execute(query, tuple(params))
        playlists = curs.fetchall()
        result = [dict(zip(columns, playlist)) for playlist in playlists] # Format the result to a usable dict
        return result
    
@router.get("/{idplaylist}")
def get_specific_playlist(
    idplaylist: int, 
):
    conn = connect_db()
    with conn.cursor() as curs:
        columns = ["id", "name", "owner_id", "track_count", "duration", "visibility", "created_at", "updated_at"]
        curs.execute("SELECT * FROM playlist WHERE idplaylist=%s", (str(idplaylist)))
        playlists = curs.fetchall()
        result = [dict(zip(columns, playlist)) for playlist in playlists] # Format the result to a usable dict
        return result