import typer

from rich.console import Console
from rich.table import Table

from src.services.track import (
    get_track,
    get_all_tracks,
    play_track,
    stop_track,
    search_tracks,
)

app = typer.Typer()
console = Console()

STATUS_STYLE = {
    "ok": "[green]ok[/green]",
    "unavailable": "[red]unavailable[/red]",
}


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
        table.add_column("status")

        for track in tracks:
            artists = ", ".join([artist.name for artist in track.artists])
            duration = (
                f"{track.durationSeconds // 60}:{track.durationSeconds % 60:02d}"
                if track.durationSeconds
                else "N/A"
            )
            status_display = STATUS_STYLE.get(track.status, track.status)
            table.add_row(
                str(track.idTrack),
                track.title,
                artists,
                duration,
                str(track.listeningCount),
                status_display,
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
        status_display = STATUS_STYLE.get(track.status, track.status)

        table.add_row("id", str(track.idTrack))
        table.add_row("title", track.title)
        table.add_row("artists", artists)
        table.add_row("duration", duration)
        table.add_row("plays", str(track.listeningCount))
        table.add_row("youtube", track.youtubeLink or "N/A")
        table.add_row("createdAt", track.createdAt.strftime("%B %d %Y"))
        table.add_row("status", status_display)

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Play a track.")
def play(id: int):
    try:
        track = get_track(id)

        if not track.is_playable():
            # Since the status can only be 'ok' or 'unavailable', if it's not playable,
            # it must be 'unavailable'.
            reason = "this track is unavailable"
            console.print(
                f"[yellow]⚠ Impossible to play '{track.title}' — {reason}.[/yellow]"
            )
            return

        play_track(id)
        console.print("[green]✓ Playback started.[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Stop a track.")
def stop():
    try:
        message = stop_track()
        if message == "No track is running.":
            console.print(f"[yellow]{message}[/yellow]")
            return
        console.print(f"[green]✓ {message}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Search tracks by title.")
def search(
    query: str = typer.Argument(..., help="Search query (partial match on title)"),
):
    try:
        tracks = search_tracks(query)

        if not tracks:
            console.print(f"[yellow]No tracks found matching '{query}'[/yellow]")
            return

        table = Table(title=f"Search results for '{query}'")
        table.add_column("id", style="cyan")
        table.add_column("title", style="magenta")
        table.add_column("artists", style="blue")
        table.add_column("duration", style="green")
        table.add_column("status")

        for track in tracks:
            artists = ", ".join([artist.name for artist in track.artists])
            duration = (
                f"{track.durationSeconds // 60}:{track.durationSeconds % 60:02d}"
                if track.durationSeconds
                else "N/A"
            )
            status_display = STATUS_STYLE.get(track.status, track.status)
            table.add_row(
                str(track.idTrack), track.title, artists, duration, status_display
            )

        console.print(table)
        console.print(f"\n[green]{len(tracks)} track(s) found[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
