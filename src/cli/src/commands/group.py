import typer
from rich.console import Console
from rich.table import Table
from src.services.group import get_user_groups

app = typer.Typer()
console = Console()


@app.command(name="list", help="List all groups available to the authenticated user.")
def list_groups():
    try:
        groups = get_user_groups()
    except Exception as e:
        console.print(f"[red] Error: {e}[/red]")
        return

    if not groups:
        console.print("[yellow]No groups found.[/yellow]")
        return

    table = Table(title="Available Groups")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")

    for group in groups:
        table.add_row(str(group.get("idGroup", "")), str(group.get("groupName", "")))

    console.print(table)
