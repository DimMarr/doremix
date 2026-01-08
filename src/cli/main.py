import typer

from commands.playlist import app as playlist_app
from commands.track import app as track_app

app = typer.Typer()

# @app.command()
# def play(name: str):
#     print(f"Hello {name}")

app.add_typer(playlist_app, name="playlist")
app.add_typer(track_app, name="track")

if __name__ == "__main__":