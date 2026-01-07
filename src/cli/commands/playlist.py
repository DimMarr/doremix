import typer

from rich.console import Console
from rich.table import Table

from services.playlist import (
    get_all_playlists,
    get_playlist,
    get_playlist_tracks,
    remove_track,
)

app = typer.Typer()
console = Console()


@app.command(help="List all playlists.")
def list():
    try:
        playlists = get_all_playlists()
    except Exception as e:
        print(e)
        return

    table = Table(title="All Playlists")

    table.add_column("id", style="cyan")
    table.add_column("title", style="magenta")

    for playlist in playlists:
        id = str(playlist.idPlaylist)
        title = playlist.name

        table.add_row(id, title)

    console.print(table)


@app.command(help="Get playlist infos.")
def get(id: str):
    try:
        playlist = get_playlist(id)
    except Exception as e:
        print(e)
        return

    table = Table(show_header=False)

    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("id", str(playlist.idPlaylist))
    table.add_row("name", playlist.name)
    table.add_row("vote", str(playlist.vote))
    table.add_row("createdAt", playlist.createdAt.strftime("%B %d %Y"))

    console.print(table)


@app.command(help="List all track from a playlist.")
def tracks(id: str):
    try:
        tracks = get_playlist_tracks(id)
    except Exception as e:
        print(e)
        return

    table = Table(title="All tracks")

    table.add_column("id", style="cyan")
    table.add_column("title", style="magenta")

    for track in tracks:
        id = str(track.idTrack)
        title = track.title

        table.add_row(id, title)

    console.print(table)


@app.command(help="Remove a track from a playlist.")
def remove(playlist_id: str, track_id: str):
    try:
        print(remove_track(playlist_id, track_id))
    except Exception as e:
        print(e)
        return
