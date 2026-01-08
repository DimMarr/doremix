import typer

from rich.console import Console
from rich.table import Table

from services.playlist import (
    get_all_playlists,
    get_playlist,
    get_playlist_tracks,
    remove_track,
    create_playlist,
    delete_playlist,
    get_playlists_by_name,
    update_playlist,
    add_track_to_playlist,
)

app = typer.Typer()
console = Console()

def select_playlist(identifier: str):

    if identifier.isdigit():
        return get_playlist(identifier)

    playlists = get_playlists_by_name(identifier)

    if len(playlists) == 1:
        return playlists[0]

    console.print(f"[yellow]Multiple playlists found with name '{identifier}':[/yellow]\n")

    table = Table(title="Choose a playlist")
    table.add_column("#", style="green")
    table.add_column("id", style="cyan")
    table.add_column("name", style="magenta")
    table.add_column("genre", style="blue")
    table.add_column("visibility", style="yellow")
    table.add_column("createdAt", style="white")

    for idx, playlist in enumerate(playlists, 1):
        table.add_row(
            str(idx),
            str(playlist.idPlaylist),
            playlist.name,
            str(playlist.idGenre),
            playlist.visibility.value,
            playlist.createdAt.strftime("%B %d %Y")
        )

    console.print(table)

    choice = typer.prompt("\nEnter the number of the playlist to select")

    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(playlists):
            return playlists[choice_idx]
        else:
            raise Exception("Invalid selection")
    except ValueError:
        raise Exception("Invalid input, please enter a number")

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

@app.command(help="Create a new playlist.")
def create(
        name: str = typer.Option(..., "--name", "-n", help="Playlist name"),
        genre: int = typer.Option(1, "--genre", "-g", help="Genre ID (1=Sans genre, 2=Rock, 3=Pop, 4=Hip-Hop, 5=Jazz, 6=Electro, 7=Metal, 8=Classical, 9=Reggae)"),
        visibility: str = typer.Option("PUBLIC", "--visibility", "-v", help="Visibility (PUBLIC, PRIVATE, OPEN, SHARED)")
        # owner: int = typer.Option(..., "--owner", "-o", help="Owner ID")  # TODO: À supprimer quand l'auth sera en place (récupéré depuis le token)
):
    try:
        playlist = create_playlist(name, genre, visibility)
        # TODO: Quand l'auth sera en place :
        # playlist = create_playlist(name, genre, visibility, current_user.id)

        console.print(f"[green]✓ Playlist créée avec succès ![/green]")

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("id", str(playlist.idPlaylist))
        table.add_row("name", playlist.name)
        table.add_row("genre", str(playlist.idGenre))
        table.add_row("visibility", playlist.visibility.value)
        table.add_row("createdAt", playlist.createdAt.strftime("%B %d %Y"))
        table.add_row("updatedAt", playlist.updatedAt.strftime("%B %d %Y"))

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗ Erreur: {e}[/red]")

@app.command(help="Delete a playlist by ID or name.")
def delete(
        identifier: str = typer.Argument(..., help="Playlist ID or name to delete"),
        force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
        # TODO: Quand l'auth sera en place, l'utilisateur sera automatiquement identifié via le token
):
    try:
        playlist = select_playlist(identifier)

        if not force:
            confirm = typer.confirm(f"Do you really want to delete the playlist '{playlist.name}'?")
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                raise typer.Abort()

        result = delete_playlist(str(playlist.idPlaylist))
        console.print(f"[green]✓ {result['message']}[/green]")

    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

@app.command(help="Update a playlist by ID or name.")
def update(
        identifier: str = typer.Argument(..., help="Playlist ID or name to update"),
        name: str = typer.Option(None, "--name", "-n", help="New playlist name"),
        genre: int = typer.Option(None, "--genre", "-g", help="New genre ID (1=Sans genre, 2=Rock, 3=Pop, 4=Hip-Hop, 5=Jazz, 6=Electro, 7=Metal, 8=Classical, 9=Reggae)"),
        visibility: str = typer.Option(None, "--visibility", "-v", help="New visibility (PUBLIC, PRIVATE, OPEN, SHARED)")
        # TODO: Quand l'auth sera en place, l'utilisateur sera automatiquement identifié via le token
):
    try:
        if name is None and genre is None and visibility is None:
            console.print("[yellow]No changes specified. Use --name, --genre, or --visibility.[/yellow]")
            raise typer.Abort()

        playlist = select_playlist(identifier)
        updated_playlist = update_playlist(str(playlist.idPlaylist), name, genre, visibility)

        console.print(f"[green]✓ Playlist successfully updated![/green]")

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("id", str(updated_playlist.idPlaylist))
        table.add_row("name", updated_playlist.name)
        table.add_row("genre", str(updated_playlist.idGenre))
        table.add_row("visibility", updated_playlist.visibility.value)
        table.add_row("createdAt", updated_playlist.createdAt.strftime("%B %d %Y"))
        table.add_row("updatedAt", updated_playlist.updatedAt.strftime("%B %d %Y"))

        console.print(table)

    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

@app.command(help="Add a track to a playlist.")
def add_track(
        identifier: str = typer.Argument(..., help="Playlist ID or name"),
        track_id: int = typer.Option(..., "--track", "-t", help="Track ID to add")
        # TODO: Quand l'auth sera en place, l'utilisateur sera automatiquement identifié via le token
):
    try:
        playlist = select_playlist(identifier)

        updated_playlist = add_track_to_playlist(str(playlist.idPlaylist), track_id)

        console.print(f"[green]✓ Track successfully added to playlist '{updated_playlist.name}'![/green]")

        tracks = get_playlist_tracks(str(updated_playlist.idPlaylist))

        table = Table(title=f"Tracks in '{updated_playlist.name}'")
        table.add_column("id", style="cyan")
        table.add_column("title", style="magenta")
        table.add_column("artists", style="blue")

        for track in tracks:
            artists = ", ".join([artist.name for artist in track.artists])
            table.add_row(str(track.idTrack), track.title, artists)

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")