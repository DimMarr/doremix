from __future__ import annotations

import typer
from rich.console import Console

from src.services.mod import add_moderator, demote_moderator
from src.utils.privileges import _require_admin

app = typer.Typer(name="mod", help="Genre management commands (Admin only).")
console = Console()


@app.command("add", help="Add a moderator.")
def add_moderator_command(id_user: int) -> None:
    _require_admin()

    try:
        add_moderator(id_user)
        console.print("[green]✓ User is now a moderator.[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command("demote", help="Demote a moderator.")
def demote_moderator_command(id_user: int) -> None:
    _require_admin()

    try:
        demote_moderator(id_user)
        console.print("[green]✓ User is no longer a moderator.[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
