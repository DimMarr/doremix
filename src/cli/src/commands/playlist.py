from typing import cast

import typer

from rich.console import Console
from rich.table import Table

from src.services.playlist import (
    PlaylistScope,
    get_all_playlists,
    get_playlist,
    get_playlist_tracks,
    remove_track,
    create_playlist,
    delete_playlist,
    update_playlist,
    add_track_to_playlist,
    search_playlists,
    search_tracks_in_playlist,
    get_shared_users,
    remove_shared_user,
    transfer_ownership,
    share_group,
    get_shared_groups,
    remove_shared_group,
    vote_playlist,
)
from src.services.group import get_user_groups

app = typer.Typer()
console = Console()


@app.command(help="List playlists.")
def list(
    scope: str = typer.Option(
        "accessible",
        "--scope",
        "-s",
        help="Scope (accessible, mine, open, public)",
    ),
):
    try:
        normalized_scope = cast(PlaylistScope, scope.lower())
        playlists = get_all_playlists(normalized_scope)
    except Exception as e:
        print(e)
        return

    table = Table(title=f"Playlists ({normalized_scope})")

    table.add_column("id", style="cyan")
    table.add_column("title", style="magenta")
    table.add_column("visibility", style="green")
    table.add_column("owner", style="yellow")

    for playlist in playlists:
        id = str(playlist.idPlaylist)
        title = playlist.name
        visibility = playlist.visibility.value
        owner = str(playlist.idOwner)

        table.add_row(id, title, visibility, owner)

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
    genre: int = typer.Option(
        1,
        "--genre",
        "-g",
        help="Genre ID (1=Sans genre, 2=Rock, 3=Pop, 4=Hip-Hop, 5=Jazz, 6=Electro, 7=Metal, 8=Classical, 9=Reggae)",
    ),
    visibility: str = typer.Option(
        "PRIVATE",
        "--visibility",
        "-v",
        help="Visibility (PUBLIC, PRIVATE, OPEN)",
    ),
    # owner: int = typer.Option(..., "--owner", "-o", help="Owner ID")  # TODO: À supprimer quand l'auth sera en place (récupéré depuis le token)
):
    try:
        playlist = create_playlist(name, genre, visibility)
        # TODO: Quand l'auth sera en place :
        # playlist = create_playlist(name, genre, visibility, current_user.id)

        console.print("[green]✓ Playlist créée avec succès ![/green]")

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


@app.command(help="Delete a playlist by ID.")
def delete(
    playlist_id: int = typer.Argument(..., help="Playlist ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    # TODO: Quand l'auth sera en place, l'utilisateur sera automatiquement identifié via le token
):
    try:
        playlist = get_playlist(str(playlist_id))

        if not force:
            confirm = typer.confirm(
                f"Do you really want to delete the playlist '{playlist.name}'?"
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                raise typer.Abort()

        result = delete_playlist(str(playlist_id))
        console.print(f"[green]✓ {result['message']}[/green]")

    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Update a playlist by ID.")
def update(
    playlist_id: int = typer.Argument(..., help="Playlist ID to update"),
    name: str = typer.Option(None, "--name", "-n", help="New playlist name"),
    genre: int = typer.Option(
        None,
        "--genre",
        "-g",
        help="New genre ID (1=Sans genre, 2=Rock, 3=Pop, 4=Hip-Hop, 5=Jazz, 6=Electro, 7=Metal, 8=Classical, 9=Reggae)",
    ),
    visibility: str = typer.Option(
        None,
        "--visibility",
        "-v",
        help="New visibility (PUBLIC, PRIVATE, OPEN)",
    ),
    # TODO: Quand l'auth sera en place, l'utilisateur sera automatiquement identifié via le token
):
    try:
        if name is None and genre is None and visibility is None:
            console.print(
                "[yellow]No changes specified. Use --name, --genre, or --visibility.[/yellow]"
            )
            raise typer.Abort()

        updated_playlist = update_playlist(str(playlist_id), name, genre, visibility)

        console.print("[green]✓ Playlist successfully updated![/green]")

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
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    youtube_link: str = typer.Option(
        ..., "--url", "-u", help="YouTube link of the track"
    ),
    title: str = typer.Option(
        ..., "--title", "-t", help="Track title (ignored if track already exists)"
    ),
    # TODO: Quand l'auth sera en place, l'utilisateur sera automatiquement identifié via le token
):
    try:
        track = add_track_to_playlist(str(playlist_id), title, youtube_link)

        console.print(f"[green]✓ Track '{track.title}' successfully added![/green]")

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
        table.add_row("youtube", track.youtubeLink or "N/A")

        console.print(table)

        playlist = get_playlist(str(playlist_id))
        tracks = get_playlist_tracks(str(playlist_id))

        tracks_table = Table(title=f"All tracks in '{playlist.name}'")
        tracks_table.add_column("id", style="cyan")
        tracks_table.add_column("title", style="magenta")
        tracks_table.add_column("artists", style="blue")

        for t in tracks:
            t_artists = ", ".join([artist.name for artist in t.artists])
            tracks_table.add_row(str(t.idTrack), t.title, t_artists)

        console.print(tracks_table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Search playlists by name.")
def search(
    query: str = typer.Argument(..., help="Search query (partial match on name)"),
):
    try:
        playlists = search_playlists(query)

        if not playlists:
            console.print(f"[yellow]No playlists found matching '{query}'[/yellow]")
            return

        table = Table(title=f"Search results for '{query}'")
        table.add_column("id", style="cyan")
        table.add_column("name", style="magenta")
        table.add_column("genre", style="blue")
        table.add_column("visibility", style="green")
        table.add_column("votes", style="yellow")

        for playlist in playlists:
            table.add_row(
                str(playlist.idPlaylist),
                playlist.name,
                str(playlist.idGenre),
                playlist.visibility.value,
                str(playlist.vote),
            )

        console.print(table)
        console.print(f"\n[green]{len(playlists)} playlist(s) found[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Search tracks in a playlist by title.")
def search_tracks(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    query: str = typer.Argument(..., help="Search query (partial match on title)"),
):
    try:
        playlist = get_playlist(str(playlist_id))
        tracks = search_tracks_in_playlist(str(playlist_id), query)

        if not tracks:
            console.print(
                f"[yellow]No tracks found matching '{query}' in playlist '{playlist.name}'[/yellow]"
            )
            return

        table = Table(title=f"Search results for '{query}' in '{playlist.name}'")
        table.add_column("id", style="cyan")
        table.add_column("title", style="magenta")
        table.add_column("artists", style="blue")
        table.add_column("duration", style="green")

        for track in tracks:
            artists = ", ".join([artist.name for artist in track.artists])
            duration = (
                f"{track.durationSeconds // 60}:{track.durationSeconds % 60:02d}"
                if track.durationSeconds
                else "N/A"
            )
            table.add_row(str(track.idTrack), track.title, artists, duration)

        console.print(table)
        console.print(f"\n[green]{len(tracks)} track(s) found[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="List users who have access to a shared playlist.")
def shared_users(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
):
    try:
        users = get_shared_users(str(playlist_id))

        if not users:
            console.print("[yellow]No users have access to this playlist.[/yellow]")
            return

        table = Table(title=f"Users with access to playlist #{playlist_id}")
        table.add_column("id", style="cyan")
        table.add_column("username", style="magenta")
        table.add_column("email", style="blue")
        table.add_column("role", style="yellow")

        for user in users:
            role = "[amber]Editor[/amber]" if user.editor else "[blue]Viewer[/blue]"
            table.add_row(str(user.idUser), user.username, user.email, role)

        console.print(table)
        console.print(f"\n[green]{len(users)} user(s) with access[/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Remove a user's access from a shared playlist.")
def unshare(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    user_id: int = typer.Argument(..., help="User ID to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    try:
        users = get_shared_users(str(playlist_id))
        target = next((u for u in users if u.idUser == user_id), None)

        if not target:
            console.print(
                f"[yellow]User #{user_id} does not have access to this playlist.[/yellow]"
            )
            return

        if not force:
            confirm = typer.confirm(
                f"Remove access for '{target.username}' ({target.email}) from playlist #{playlist_id}?"
            )
            if not confirm:
                console.print("[yellow]Cancelled.[/yellow]")
                raise typer.Abort()

        result = remove_shared_user(str(playlist_id), str(user_id))
        console.print(f"[green]✓ {result['message']}[/green]")

    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="Transfer ownership of a playlist to another user (by email).")
def transfer(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    email: str = typer.Option(..., "--email", "-e", help="New owner email"),
):
    try:
        playlist = get_playlist(str(playlist_id))

        confirm = typer.confirm(
            f"Do you really want to transfer ownership of '{playlist.name}' to {email}? This action is irreversible."
        )
        if not confirm:
            console.print("[yellow]Transfer cancelled.[/yellow]")
            raise typer.Abort()

        result = transfer_ownership(str(playlist_id), email)

        console.print("[green]Ownership transferred successfully![/green]")

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("playlist_id", str(playlist_id))
        table.add_row("new_owner", email)
        table.add_row("message", result.get("message", "Success"))

        console.print(table)

    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command(help="Share a playlist with a group.")
def share_to_group(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    group_id: int = typer.Option(..., "--group", "-g", help="Group ID"),
):
    try:
        from src.services.group import get_user_groups

        groups = get_user_groups()
        target_group = next((g for g in groups if g.get("idGroup") == group_id), None)

        if not target_group:
            console.print(
                f"[red] Error: Group with ID {group_id} not found or you are not a member.[/red]"
            )
            raise typer.Exit(1)

        group_name = target_group.get("groupName")

        response = share_group(str(playlist_id), group_name)
        if response.get("message") == "Playlist is already shared with this group":
            console.print(
                f"[yellow]ℹ Playlist is already shared with group '{group_name}'[/yellow]"
            )
        else:
            console.print(
                f"[green] Playlist successfully shared with group '{group_name}'[/green]"
            )
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(help="List groups who have access to a shared playlist.")
def shared_groups(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
):
    try:
        groups = get_shared_groups(str(playlist_id))

        if not groups:
            console.print("[yellow]No groups have access to this playlist.[/yellow]")
            return

        table = Table(title=f"Groups with access to playlist #{playlist_id}")
        table.add_column("id", style="cyan")
        table.add_column("group_name", style="magenta")

        for group in groups:
            table.add_row(str(group.idGroup), group.groupName)

        console.print(table)
        console.print(f"[green]{len(groups)} group(s) with access[/green]")

    except Exception as e:
        console.print(f"[red] Error: {e}[/red]")


@app.command(help="Remove a group's access from a shared playlist.")
def unshare_group(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    group_id: int = typer.Argument(..., help="Group ID to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    try:
        groups = get_shared_groups(str(playlist_id))
        target = next((g for g in groups if g.idGroup == group_id), None)

        if not target:
            console.print(
                f"[yellow]Group #{group_id} does not have access to this playlist.[/yellow]"
            )
            return

        if not force:
            confirm = typer.confirm(
                f"Remove access for '{target.groupName}' from playlist #{playlist_id}?"
            )
            if not confirm:
                console.print("[yellow]Cancelled.[/yellow]")
                raise typer.Abort()

        result = remove_shared_group(str(playlist_id), str(group_id))
        console.print(f"[green] {result.get('message', 'Success')}[/green]")

    except Exception as e:
        console.print(f"[red] Error: {e}[/red]")

@app.command(help="Vote on a playlist (upvote, downvote, or remove vote).")
def vote(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    upvote: bool = typer.Option(False, "--up", "-u", help="Upvote the playlist"),
    downvote: bool = typer.Option(False, "--down", "-d", help="Downvote the playlist"),
    remove: bool = typer.Option(False, "--remove", "-r", help="Remove your vote"),
):
    try:
        if sum([upvote, downvote, remove]) != 1:
            console.print(
                "[yellow]Specify exactly one of --up, --down, or --remove.[/yellow]"
            )
            raise typer.Abort()

        value = 1 if upvote else (-1 if downvote else 0)
        result = vote_playlist(str(playlist_id), value)

        score = result.get("score", "?")
        user_vote = result.get("userVote")

        if value == 1:
            console.print(f"[green]Upvoted![/green] Score: {score}")
        elif value == -1:
            console.print(f"[red]Downvoted![/red] Score: {score}")
        else:
            console.print(f"[yellow]Vote removed.[/yellow] Score: {score}")

        if user_vote is not None:
            vote_label = (
                "+1" if user_vote == 1 else ("-1" if user_vote == -1 else "none")
            )
            console.print(f"Your vote: {vote_label}")

    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red] Error: {e}[/red]")
