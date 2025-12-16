from pytubefix import YouTube
import vlc
import requests

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable
from textual.binding import Binding

instance = vlc.Instance('--quiet')
player = instance.media_player_new()

def stream_youtube(url):
    yt = YouTube(url)
    audio_stream = yt.streams.get_audio_only()
    audio_url = audio_stream.url

    media = instance.media_new(audio_url)
    player.set_media(media)
    player.play()

class PlaylistApp(App):    

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield DataTable()
    
    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        
        # Add columns
        table.add_column("#")
        table.add_column("Name")
        table.add_column("idGenre")
        table.add_column("idOwner")
        
        # Add rows
        request = requests.get(f'http://localhost:8000/playlists/')
        playlists = request.json()
        for playlist in playlists:
            table.add_row(
                playlist['idPlaylist'],
                playlist['name'],
                playlist['idGenre'],
                playlist['idOwner'],
                key=str(playlist['idPlaylist'])
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        playlistId = event.row_key.value
        self.push_screen(PlaylistScreen(playlistId))

class PlaylistScreen(Screen):
    def __init__(self, playlistId):
        super().__init__()
        self.playlistId = playlistId

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("p", "play_track", "Play"),
        Binding("space", "pause_track", "Pause Track")
    ]

    def compose(self) -> ComposeResult:
        yield DataTable()
    
    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        
        table.add_column("Title", width=30)
        table.add_column("Artist(s)", width=20)
        table.add_column("Listening Count", width=30)
        table.add_column("Duration", width=10)
        table.add_column("Youtube Link")

        
        request = requests.get(f'http://localhost:8000/playlists/{self.playlistId}/tracks')
        playlist = request.json()
        for music in playlist:
            table.add_row(
                music['title'],
                ", ".join(artist['name'] for artist in music['artists']),
                music['listeningCount'],
                music['durationSeconds'],
                music['youtubeLink'],
                key=music['youtubeLink']
            )

    def action_play_track(self) -> None:
        table = self.query_one(DataTable)
        row = table.get_row_at(table.cursor_row)
        youtube_link = row[4]
        song_title = row[0]
        self.notify(f'Starting : {song_title}')
        stream_youtube(youtube_link)

    def action_pause_track(self) -> None:
        player.pause()

if __name__ == "__main__":
    app = PlaylistApp()
    app.run()