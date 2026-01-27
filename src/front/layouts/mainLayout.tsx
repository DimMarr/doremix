import { Header } from "@components/generics/index";
import { initializePlayer, TrackPlayer } from "@components/playlists/trackPlayer";
import YoutubePlayer from "@store/trackPlayer";
import { waitForYouTubeAPI } from "@utils/youtubeApiLoader";
import logo from "@assets/images/logo.png";
import Playlist from "@models/playlist";

export let trackPlayerInstance = null;

export async function createMainLayout() {
  const root = document.getElementById("app") || document.body;

  await waitForYouTubeAPI();

  const appHtml = (
    <div class="min-h-screen bg-background text-foreground px-6">
      <Header className="">
        <a href="/">
          <img src={logo} alt="Dorémix" class="h-8" />
        </a>
      </Header>

      <main class="" id="mainContent"></main>

      <div id="youtubePlayer"></div>
      <div id="trackPlayerContainer">{TrackPlayer()}</div>
    </div>
  );

  root.innerHTML = appHtml;
  const mainContent = document.getElementById("mainContent");

  // Initialisation du TrackPlayer
  const trackPlayer = new YoutubePlayer({
    playlist: new Playlist({tracks:[]}),
    youtubePlayerHtmlElementId: "youtubePlayer",
  });

  trackPlayerInstance = trackPlayer;

  // Rendering du track player.
  const trackPlayerContainer = document.getElementById("trackPlayerContainer");
  if (trackPlayerContainer) {
    initializePlayer(trackPlayerContainer!, trackPlayer);
  }

  return { mainContent, trackPlayer };
}
