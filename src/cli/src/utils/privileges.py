from __future__ import annotations

import typer
from rich.console import Console
from src.utils.token_storage import get_user
from src.utils.exceptions import (
    ForbiddenError,
    NotAuthenticatedError,
)

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
