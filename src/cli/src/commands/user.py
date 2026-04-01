import typer
from rich.console import Console
from rich.table import Table

from src.services.user import unban, can_be_unbanned_list, can_be_banned_list, ban


app = typer.Typer()
console = Console()


def display_list(users):
    table = Table(title="Unban Candidates")
    table.add_column("ID", style="cyan")
    table.add_column("Username", style="magenta")
    table.add_column("Email", style="green")

    for user in users:
        # Gestion sécurisée que ce soit un dictionnaire ou un objet Pydantic
        user_id = (
            user.get("idUser", "N/A")
            if isinstance(user, dict)
            else getattr(user, "idUser", "N/A")
        )
        username = (
            user.get("username", "N/A")
            if isinstance(user, dict)
            else getattr(user, "username", "N/A")
        )
        email = (
            user.get("email", "N/A")
            if isinstance(user, dict)
            else getattr(user, "email", "N/A")
        )
        table.add_row(str(user_id), str(username), str(email))

    console.print(table)


@app.command(name="ban-candidates", help="List users that can be banned.")
def ban_candidates():
    try:
        users = can_be_banned_list()
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return

    if not users:
        console.print("[yellow]No users found that can be banned.[/yellow]")
        return

    display_list(users)


@app.command(name="unban-candidates", help="List users that can be unbanned.")
def unban_candidates():
    try:
        users = can_be_unbanned_list()
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        return

    if not users:
        console.print("[yellow]No users found that can be unbanned.[/yellow]")
        return

    display_list(users)


@app.command(name="ban", help="Ban a user by their ID.")
def ban_user(user_id: int = typer.Argument(..., help="ID of the user to ban")):
    try:
        ban(user_id)
        console.print(f"[green]✓ User {user_id} has been successfully banned![/green]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")


@app.command(name="unban", help="Unban a user by their ID.")
def unban_user(user_id: int = typer.Argument(..., help="ID of the user to unban")):
    try:
        unban(user_id)
        console.print(
            f"[green]✓ User {user_id} has been successfully unbanned![/green]"
        )
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
