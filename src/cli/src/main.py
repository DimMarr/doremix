import click
from typer.main import get_command

from src.commands.playlist import app as playlist_app
from src.commands.track import app as track_app
from src.commands.auth import auth as auth_group


@click.group()
def app() -> None:
    """DoReMix CLI."""


app.add_command(get_command(playlist_app), name="playlist")
app.add_command(get_command(track_app), name="track")
app.add_command(auth_group.commands["register"], name="register")
app.add_command(auth_group.commands["login"], name="login")
app.add_command(auth_group.commands["whoami"], name="whoami")
app.add_command(auth_group.commands["logout"], name="logout")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
