import { Header } from "@components/generics/index";
import { initializePlayer, TrackPlayer } from "@components/playlists/trackPlayer";
import YoutubePlayer from "@store/trackPlayer";
import { waitForYouTubeAPI } from "@utils/youtubeApiLoader";
import logo from "@assets/images/logo.png";
import Playlist from "@models/playlist";
import { authService } from "@utils/authentication";
import { AppRoutes } from "../router";
export let trackPlayerInstance = null;

export async function createMainLayout() {
  const root = document.getElementById("app") || document.body;

  await waitForYouTubeAPI();
  let isAuth = await authService.isAuthenticated();

  const appHtml = (
    <div class="min-h-screen bg-background text-foreground px-6 pb-20">
      <Header className="">
        <a href="/" style={window.location.pathname === AppRoutes.LOGIN || window.location.pathname === AppRoutes.SIGNUP ? 'display: none;' : ''}>
          <img src={logo} alt="Dorémix" class="h-8" />
        </a>

        {isAuth &&
          <nav class="flex ml-6 gap-4 border-l pl-6 border-white/10 items-center justify-center mr-auto">
            <a href="/" class="text-sm font-semibold transition-colors text-white/60 hover:text-white nav-link" data-link>Playlists</a>
            <a href="/artists" class="text-sm font-semibold transition-colors text-white/60 hover:text-white nav-link" data-link>Artists</a>
          </nav>
        }

        {isAuth &&
          <div>
            <svg id="logout" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 cursor-pointer">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l-3 3m0 0 3 3m-3-3h12.75" />
            </svg>
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

    if (btn) {
      btn.addEventListener('click', async () => {
        await authService.logout()
        window.location.href = AppRoutes.LOGIN
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
