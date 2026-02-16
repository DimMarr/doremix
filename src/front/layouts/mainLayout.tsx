import { Header } from "@components/generics/index";
import { initializePlayer, TrackPlayer } from "@components/playlists/trackPlayer";
import YoutubePlayer from "@store/trackPlayer";
import { waitForYouTubeAPI } from "@utils/youtubeApiLoader";
import logo from "@assets/images/logo.png";
import Playlist from "@models/playlist";
import { authService } from "@utils/authentication";
export let trackPlayerInstance = null;

export async function createMainLayout() {
  const root = document.getElementById("app") || document.body;

  await waitForYouTubeAPI();
  let isAuth = await authService.isAuthenticated();

  const appHtml = (
    <div class="min-h-screen bg-background text-foreground px-6 pb-20">
      <Header className="">
        <a href="/">
          <img src={logo} alt="Dorémix" class="h-8" />
        </a>

        {isAuth &&
          <div>
            <span id="logout" class="cursor-pointer">Log out</span>
            <img src="../../assets/icons/logout.png" alt="" />
          </div>}
      </Header>

      <main class="" id="mainContent"></main>

      <div id="youtubePlayer"></div>
      <div id="trackPlayerContainer">{TrackPlayer()}</div>
    </div>
  );

  root.innerHTML = appHtml;
  const mainContent = document.getElementById("mainContent");

  // Gestion de la deconnexion
  const logout = async () => {
    const btn = document.getElementById("logout")

    if(btn){
      btn.addEventListener('click', async () => {
        await authService.logout()
        window.location.href = "/login"
        return
      })
    }
  }
  logout();

  // Initialisation du TrackPlayer
  const trackPlayer = new YoutubePlayer({
    playlist: new Playlist({ tracks: [] }),
    youtubePlayerHtmlElementId: "youtubePlayer",
  });

  trackPlayerInstance = trackPlayer;

  // Rendering du track player
  const trackPlayerContainer = document.getElementById("trackPlayerContainer");
  if (trackPlayerContainer) {
    initializePlayer(trackPlayerContainer!, trackPlayer);
  }

  return { mainContent, trackPlayer };
}
