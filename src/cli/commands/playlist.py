import typer

from rich.console import Console
from rich.table import Table

from services.playlist import get_all_playlists, get_playlist, get_playlist_tracks

app = typer.Typer()
console = Console()

@app.command(help="List all playlists.")
def list():
    playlists = get_all_playlists()

    table = Table(title="All Playlists")

    table.add_column("id", style="cyan")
    table.add_column("title", style="magenta")

    for playlist in playlists:
        id = str(playlist.idPlaylist)
        title = playlist.name
        
        table.add_row(id, title)

    console.print(table)

@app.command(help="Get playlist infos.")
def get(id: int):
    try:
        playlist = get_playlist(id)
    except:
        raise typer.BadParameter(f"Playlist n°{id} not found.")
    
    table = Table(show_header=False)

    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("id", str(playlist.idPlaylist))
    table.add_row("name", playlist.name)
    table.add_row("vote", str(playlist.vote))
    table.add_row("createdAt", playlist.createdAt.strftime("%B %d %Y"))

    console.print(table)

@app.command(help="List all track from a playlist.")
def tracks(id: int):
    tracks = get_playlist_tracks(id)

    table = Table(title="All tracks")

    table.add_column("id", style="cyan")
    table.add_column("title", style="magenta")

    for track in tracks:
        id = str(track.idTrack)
        title = track.title
        
        table.add_row(id, title)

    console.print(table)