import typer

from rich.console import Console
from rich.table import Table

from services.track import get_track, play_track, stop_track

app = typer.Typer()
console = Console()


@app.command(help="Get infos about a track.")
def get(id: int):
    try:
        track = get_track(id)
    except Exception:
        print("Track not found.")
        return

    table = Table(show_header=False)

    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("id", str(track.idTrack))
    table.add_row("title", track.title)
    table.add_row("listeningCount", str(track.listeningCount))
    table.add_row("durationSeconds", str(track.durationSeconds))

    console.print(table)


@app.command(help="Play a track.")
def play(id: int):
    return play_track(id)


@app.command(help="Stop a track.")
def stop():
    return stop_track()
