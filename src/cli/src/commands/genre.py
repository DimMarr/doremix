from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from src.services.genre import get_all, create, update, delete
from src.utils.privileges import _require_admin
from src.utils.exceptions import (
    ApiRequestError,
    GenreExistsError,
    GenreNotFoundError,
    NotAuthenticatedError,
)

app = typer.Typer(name="genres", help="Genre management commands (Admin only).")
console = Console()


@app.command("list", help="List all available musical genres.")
def list_command() -> None:
    _require_admin()

    try:
        genres = get_all()
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


@app.command("add", help="Create a new genre.")
def add_command(
    label: str = typer.Option(
        ..., "--label", "-l", prompt=True, help="The name of the new genre."
    ),
) -> None:
    _require_admin()

    clean_label = label.strip()

    try:
        existing_genres = get_all()
        if any(g.label.strip().lower() == clean_label.lower() for g in existing_genres):
            console.print("[yellow]⚠ This genre already exists.[/yellow]")
            return

        new_genre = create(label=clean_label)
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


@app.command("update", help="Update an existing genre's label.")
def update_command(
    genre_id: int = typer.Argument(..., help="The ID of the genre to update."),
    label: str = typer.Option(
        ..., "--label", "-l", prompt=True, help="The new name for the genre."
    ),
) -> None:
    _require_admin()

    clean_label = label.strip()

    try:
        existing_genres = get_all()
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

        updated_genre = update(genre_id=genre_id, label=clean_label)
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


@app.command("delete", help="Delete a genre from the database.")
def delete_command(
    genre_id: int = typer.Argument(..., help="The ID of the genre to delete."),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    _require_admin()

    try:
        existing_genres = get_all()
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

        delete(genre_id=genre_id)
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
