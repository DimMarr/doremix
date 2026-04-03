from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from src.services.admin_playlist import (
    get_all_playlists,
    get_playlist_tracks,
    update_playlist,
    delete_playlist,
    add_track,
    remove_track,
)
from src.services.admin_group import (
    add_user_to_group,
    create_group,
    delete_group,
    get_user_display_name,
    get_all_groups,
    remove_user_from_group,
)
from src.services.genre import get_all as genre_get_all, create as genre_create
from src.services.genre import update as genre_update, delete as genre_delete
from src.utils.token_storage import get_user
from src.utils.exceptions import (
    ApiRequestError,
    ForbiddenError,
    GroupExistsError,
    GroupMembershipError,
    GroupNotFoundError,
    GenreExistsError,
    GenreNotFoundError,
    NotAuthenticatedError,
    PlaylistNotFoundError,
    UserNotFoundError,
)

admin_app = typer.Typer(help="Admin commands.")
playlist_app = typer.Typer(help="Admin playlist management commands.")
genre_app = typer.Typer(help="Genre management commands (Admin only).")
group_app = typer.Typer(help="Group management commands (Admin only).")

admin_app.add_typer(playlist_app, name="playlist")
admin_app.add_typer(genre_app, name="genre")
admin_app.add_typer(group_app, name="group")

console = Console()


def _require_admin() -> None:
    try:
        user = get_user()
        if user.get("role") != "ADMIN":
            raise ForbiddenError(
                "Access denied. This command requires Administrator privileges."
            )
    except NotAuthenticatedError as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except ForbiddenError as exc:
        console.print(f"[red]✗ {exc}[/red]")
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# Playlist commands
# ---------------------------------------------------------------------------


@playlist_app.command("list")
def playlist_list() -> None:
    """List all playlists (admin view)."""
    _require_admin()

    try:
        playlists = get_all_playlists()
        if not playlists:
            console.print("[yellow]No playlists found.[/yellow]")
            return

        table = Table(title="All Playlists (Admin)")
        table.add_column("id", style="cyan")
        table.add_column("name", style="magenta")
        table.add_column("visibility", style="green")
        table.add_column("owner", style="yellow")

        for p in playlists:
            table.add_row(str(p.idPlaylist), p.name, p.visibility.value, str(p.idOwner))

        console.print(table)

    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@playlist_app.command("tracks")
def playlist_tracks(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
) -> None:
    """List tracks in a playlist."""
    _require_admin()

    try:
        tracks = get_playlist_tracks(playlist_id)
        if not tracks:
            console.print("[yellow]No tracks in this playlist.[/yellow]")
            return

        table = Table(title=f"Tracks in playlist {playlist_id}")
        table.add_column("id", style="cyan")
        table.add_column("title", style="magenta")

        for t in tracks:
            table.add_row(str(t.idTrack), t.title)

        console.print(table)

    except PlaylistNotFoundError:
        console.print(f"[yellow]⚠ Playlist {playlist_id} not found.[/yellow]")
    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@playlist_app.command("update")
def playlist_update(
    playlist_id: int = typer.Argument(..., help="Playlist ID to update"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="New name"),
    genre: Optional[int] = typer.Option(None, "--genre", "-g", help="New genre ID"),
    visibility: Optional[str] = typer.Option(
        None, "--visibility", "-v", help="New visibility (PUBLIC, PRIVATE, OPEN)"
    ),
) -> None:
    """Update a playlist."""
    _require_admin()

    if name is None and genre is None and visibility is None:
        console.print(
            "[yellow]No changes specified. Use --name, --genre, or --visibility.[/yellow]"
        )
        raise typer.Abort()

    try:
        updated = update_playlist(
            playlist_id, name=name, id_genre=genre, visibility=visibility
        )
        console.print("[green]✓ Playlist successfully updated![/green]")

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("id", str(updated.idPlaylist))
        table.add_row("name", updated.name)
        table.add_row("genre", str(updated.idGenre))
        table.add_row("visibility", updated.visibility.value)
        table.add_row("createdAt", updated.createdAt.strftime("%B %d %Y"))
        table.add_row("updatedAt", updated.updatedAt.strftime("%B %d %Y"))

        console.print(table)

    except PlaylistNotFoundError:
        console.print(f"[yellow]⚠ Playlist {playlist_id} not found.[/yellow]")
    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@playlist_app.command("delete")
def playlist_delete(
    playlist_id: int = typer.Argument(..., help="Playlist ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a playlist."""
    _require_admin()

    try:
        if not force:
            confirm = typer.confirm(
                f"Do you really want to delete playlist {playlist_id}?"
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                raise typer.Abort()

        delete_playlist(playlist_id)
        console.print(f"[green]✓ Playlist {playlist_id} deleted successfully.[/green]")

    except PlaylistNotFoundError:
        console.print(f"[yellow]⚠ Playlist {playlist_id} not found.[/yellow]")
    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@playlist_app.command("add-track")
def playlist_add_track(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    url: str = typer.Option(..., "--url", "-u", help="YouTube URL of the track"),
    title: str = typer.Option(..., "--title", "-t", help="Track title"),
) -> None:
    """Add a track to a playlist."""
    _require_admin()

    try:
        track = add_track(playlist_id, title=title, url=url)
        console.print(
            f"[green]✓ Track '{track.title}' added to playlist {playlist_id}.[/green]"
        )

        tracks = get_playlist_tracks(playlist_id)

        table = Table(title=f"Tracks in playlist {playlist_id}")
        table.add_column("id", style="cyan")
        table.add_column("title", style="magenta")

        for t in tracks:
            table.add_row(str(t.idTrack), t.title)

        console.print(table)

    except PlaylistNotFoundError:
        console.print(f"[yellow]⚠ Playlist {playlist_id} not found.[/yellow]")
    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@playlist_app.command("remove-track")
def playlist_remove_track(
    playlist_id: int = typer.Argument(..., help="Playlist ID"),
    track_id: int = typer.Argument(..., help="Track ID to remove"),
) -> None:
    """Remove a track from a playlist."""
    _require_admin()

    try:
        remove_track(playlist_id, track_id)
        console.print(
            f"[green]✓ Track {track_id} removed from playlist {playlist_id}.[/green]"
        )

        tracks = get_playlist_tracks(playlist_id)

        table = Table(title=f"Tracks in playlist {playlist_id}")
        table.add_column("id", style="cyan")
        table.add_column("title", style="magenta")

        for t in tracks:
            table.add_row(str(t.idTrack), t.title)

        console.print(table)

    except PlaylistNotFoundError:
        console.print(f"[yellow]⚠ Playlist {playlist_id} not found.[/yellow]")
    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


# ---------------------------------------------------------------------------
# Genre commands (migrated verbatim from commands/genre.py)
# ---------------------------------------------------------------------------


@genre_app.command("list", help="List all available musical genres.")
def genre_list_command() -> None:
    _require_admin()

    try:
        genres = genre_get_all()
        if not genres:
            console.print("[yellow]No genres found in the database.[/yellow]")
            return

        table = Table(title="Available Genres")
        table.add_column("id", style="cyan")
        table.add_column("label", style="magenta")

        for genre in genres:
            table.add_row(str(genre.idGenre), genre.label)

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@genre_app.command("add", help="Create a new genre.")
def genre_add_command(
    label: str = typer.Option(
        ..., "--label", "-l", prompt=True, help="The name of the new genre."
    ),
) -> None:
    _require_admin()

    clean_label = label.strip()

    try:
        existing_genres = genre_get_all()
        if any(g.label.strip().lower() == clean_label.lower() for g in existing_genres):
            console.print("[yellow]⚠ This genre already exists.[/yellow]")
            return

        new_genre = genre_create(label=clean_label)
        console.print(
            f"[green]✓ Genre '{new_genre.label}' created successfully![/green]"
        )

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("id", str(new_genre.idGenre))
        table.add_row("label", new_genre.label)

        console.print(table)

    except (GenreExistsError, NotAuthenticatedError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@genre_app.command("update", help="Update an existing genre's label.")
def genre_update_command(
    genre_id: int = typer.Argument(..., help="The ID of the genre to update."),
    label: str = typer.Option(
        ..., "--label", "-l", prompt=True, help="The new name for the genre."
    ),
) -> None:
    _require_admin()

    clean_label = label.strip()

    try:
        existing_genres = genre_get_all()
        current_genre = next(
            (g for g in existing_genres if g.idGenre == genre_id), None
        )

        if not current_genre:
            console.print(f"[yellow]⚠ Genre with ID {genre_id} not found.[/yellow]")
            return

        if current_genre.label.strip().lower() == clean_label.lower():
            console.print(
                f"[yellow] No changes needed. The genre is already named '{current_genre.label}'.[/yellow]"
            )
            return

        if any(
            g.label.strip().lower() == clean_label.lower()
            for g in existing_genres
            if g.idGenre != genre_id
        ):
            console.print(
                f"[yellow]⚠ Another genre already uses the name '{clean_label}'.[/yellow]"
            )
            return

        updated_genre = genre_update(genre_id=genre_id, label=clean_label)
        console.print("[green]✓ Genre successfully updated![/green]")

        table = Table(show_header=False)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("id", str(updated_genre.idGenre))
        table.add_row("label", updated_genre.label)

        console.print(table)

    except (GenreNotFoundError, GenreExistsError, NotAuthenticatedError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@genre_app.command("delete", help="Delete a genre from the database.")
def genre_delete_command(
    genre_id: int = typer.Argument(..., help="The ID of the genre to delete."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    _require_admin()

    try:
        existing_genres = genre_get_all()
        target_genre = next((g for g in existing_genres if g.idGenre == genre_id), None)

        if not target_genre:
            console.print(
                f"[yellow]⚠ Genre with ID {genre_id} not found. Deletion aborted.[/yellow]"
            )
            return

        if not force:
            confirm = typer.confirm(
                f"Do you really want to delete the genre '{target_genre.label}' (ID: {genre_id})?"
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                raise typer.Abort()

        genre_delete(genre_id=genre_id)
        console.print(
            f"[green]✓ Genre '{target_genre.label}' (ID: {genre_id}) deleted successfully.[/green]"
        )

    except typer.Abort:
        pass
    except ApiRequestError as exc:
        if "linked" in str(exc) or "used" in str(exc):
            console.print(f"[bold red]✗ Constraint Error:[/bold red] [red]{exc}[/red]")
            console.print(
                "[red]Suggestion: Remove this genre from all playlists before trying to delete it.[/red]"
            )
        else:
            console.print(f"[red]✗ API Error: {exc}[/red]")
    except (GenreNotFoundError, NotAuthenticatedError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Unexpected Error: {e}[/red]")


# ---------------------------------------------------------------------------
# Group commands
# ---------------------------------------------------------------------------


@group_app.command("list", help="List groups and their members.")
def group_list_command() -> None:
    _require_admin()

    try:
        groups = get_all_groups()
        if not groups:
            console.print("[yellow]No groups found.[/yellow]")
            return

        for group in groups:
            table = Table(title=f"Group #{group.idGroup} - {group.groupName}")
            table.add_column("user_id", style="cyan")
            table.add_column("username", style="magenta")
            table.add_column("email", style="yellow")

            if not group.users:
                table.add_row("-", "(no members)", "-")
            else:
                for member in group.users:
                    table.add_row(
                        str(member.idUser),
                        member.username,
                        member.email,
                    )

            console.print(table)

    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@group_app.command("create", help="Create a new group.")
def group_create_command(
    name: str = typer.Option(..., "--name", "-n", prompt=True, help="Group name"),
) -> None:
    _require_admin()

    clean_name = name.strip()
    if not clean_name:
        console.print("[yellow]⚠ Group name cannot be empty.[/yellow]")
        raise typer.Exit(code=1)

    try:
        existing_groups = get_all_groups()
        if any(
            g.groupName.strip().lower() == clean_name.lower() for g in existing_groups
        ):
            console.print("[yellow]⚠ A group with this name already exists.[/yellow]")
            return

        group = create_group(clean_name)
        console.print(
            f"[green]✓ Group '{group.groupName}' created successfully (id={group.idGroup}).[/green]"
        )

    except GroupExistsError:
        console.print("[yellow]⚠ A group with this name already exists.[/yellow]")
    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@group_app.command("delete", help="Delete an existing group.")
def group_delete_command(
    group_id: int = typer.Argument(..., help="Group ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    _require_admin()

    try:
        if not force:
            if not typer.confirm(f"Do you really want to delete group {group_id}?"):
                console.print("[yellow]Deletion cancelled.[/yellow]")
                raise typer.Abort()

        delete_group(group_id)
        console.print(f"[green]✓ Group {group_id} deleted successfully.[/green]")

    except GroupNotFoundError:
        console.print(f"[yellow]⚠ Group {group_id} not found.[/yellow]")
    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except typer.Abort:
        pass
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@group_app.command("add-user", help="Add a user to a group.")
def group_add_user_command(
    group_id: int = typer.Argument(..., help="Group ID"),
    user_id: int = typer.Argument(..., help="User ID"),
) -> None:
    _require_admin()

    user_label = f"User {user_id}"
    try:
        user_label = get_user_display_name(user_id)
    except UserNotFoundError:
        console.print(f"[yellow]⚠ User {user_id} not found.[/yellow]")
        return
    except Exception:
        # Keep command functional even if user lookup fails for non-critical reasons
        user_label = f"User {user_id}"

    try:
        add_user_to_group(group_id, user_id)
        console.print(
            f"[green]✓ {user_label} added to group {group_id} successfully.[/green]"
        )
    except GroupMembershipError as exc:
        message = str(exc).lower()
        if "already" in message:
            console.print(
                f"[yellow]⚠ {user_label} is already in group {group_id}.[/yellow]"
            )
        else:
            console.print(f"[yellow]⚠ {exc}[/yellow]")
    except UserNotFoundError:
        console.print(f"[yellow]⚠ User {user_id} not found.[/yellow]")
    except GroupNotFoundError:
        console.print(f"[yellow]⚠ Group {group_id} not found.[/yellow]")
    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@group_app.command("remove-user", help="Remove a user from a group.")
def group_remove_user_command(
    group_id: int = typer.Argument(..., help="Group ID"),
    user_id: int = typer.Argument(..., help="User ID"),
) -> None:
    _require_admin()

    try:
        remove_user_from_group(group_id, user_id)
        console.print(
            f"[green]✓ User {user_id} removed from group {group_id} successfully.[/green]"
        )
    except GroupMembershipError as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
    except UserNotFoundError:
        console.print(f"[yellow]⚠ User {user_id} not found.[/yellow]")
    except GroupNotFoundError:
        console.print(f"[yellow]⚠ Group {group_id} not found.[/yellow]")
    except (NotAuthenticatedError, ForbiddenError) as exc:
        console.print(f"[yellow]⚠ {exc}[/yellow]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
