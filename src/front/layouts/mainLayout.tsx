import { Badge, Button, Header } from "@components/generics/index";
import { initializePlayer, TrackPlayer } from "@components/playlists/track-player";
import PlaylistRepository from "@repositories/playlistRepository";
import YoutubePlayer from "@store/track-player";
import { waitForYouTubeAPI } from "@utils/youtube-api-loader";
import logo from "@assets/images/logo.png";

export async function createMainLayout() {
  const root = document.getElementById("app") || document.body;

  const repo = new PlaylistRepository();
  const playlists = await repo.getPlaylists();

  await waitForYouTubeAPI();

  // First, render the HTML to the DOM
  const appHtml = (
    <div class="min-h-screen bg-background text-foreground px-6">
      <Header className="">
        <img src={logo} alt="Dorémix" class="h-8" />
        <div class="flex gap-2">
          <Button variant="outline" size="sm">Login</Button>
          <Button variant="primary" size="sm">Signup</Button>
        </div>
      </Header>

      <main class="" id="mainContent"></main>

      <div id="youtubePlayer"></div>
      <div id="trackPlayerContainer">{TrackPlayer()}</div>
    </div>
  );

  root.innerHTML = appHtml;
  const mainContent = document.getElementById("mainContent");

  // Now create the player AFTER the iframe exists in the DOM
  const trackPlayer = new YoutubePlayer({
    playlist: playlists[0],
    youtubePlayerHtmlElementId: "youtubePlayer",
  });

  // Render the track player component
  const trackPlayerContainer = document.getElementById("trackPlayerContainer");
  if (trackPlayerContainer) {
    initializePlayer(trackPlayerContainer!, trackPlayer);
  }

  return { mainContent, trackPlayer };
}
