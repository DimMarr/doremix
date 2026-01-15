import typer

from rich.console import Console
from rich.table import Table

from services.track import get_track, get_all_tracks, play_track, stop_track

app = typer.Typer()
console = Console()


@app.command(help="List all tracks.")
def list():
    try:
        tracks = get_all_tracks()

        table = Table(title="All Tracks")
        table.add_column("id", style="cyan")
        table.add_column("title", style="magenta")
        table.add_column("artists", style="blue")
        table.add_column("duration", style="green")
        table.add_column("plays", style="yellow")

        for track in tracks:
            artists = ", ".join([artist.name for artist in track.artists])
            duration = (
                f"{track.durationSeconds // 60}:{track.durationSeconds % 60:02d}"
                if track.durationSeconds
                else "N/A"
            )
            table.add_row(
                str(track.idTrack),
                track.title,
                artists,
                duration,
                str(track.listeningCount),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Get track info.")
def get(id: int = typer.Argument(..., help="Track ID")):
    try:
        track = get_track(id)

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        artists = ", ".join([artist.name for artist in track.artists])
        duration = (
            f"{track.durationSeconds // 60}:{track.durationSeconds % 60:02d}"
            if track.durationSeconds
            else "N/A"
        )

        table.add_row("id", str(track.idTrack))
        table.add_row("title", track.title)
        table.add_row("artists", artists)
        table.add_row("duration", duration)
        table.add_row("plays", str(track.listeningCount))
        table.add_row("youtube", track.youtubeLink or "N/A")
        table.add_row("createdAt", track.createdAt.strftime("%B %d %Y"))

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Play a track.")
def play(id: int):
    return play_track(id)


@app.command(help="Stop a track.")
def stop():
    return stop_track()
