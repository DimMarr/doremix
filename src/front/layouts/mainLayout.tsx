import { Badge, Button, Header } from "@components/generics/index";
import { initializePlayer, TrackPlayer } from "@components/playlists/track-player";
import PlaylistRepository from "@repositories/playlistRepository";
import YoutubePlayer from "@store/track-player";
import { AuthStore } from "@store/auth";
import { waitForYouTubeAPI } from "@utils/youtube-api-loader";
import logo from "@assets/images/logo.png";

export async function createMainLayout(authStore: AuthStore, router: any) {
  const root = document.getElementById("app") || document.body;

  const repo = new PlaylistRepository();
  const playlists = await repo.getPlaylists();

  await waitForYouTubeAPI();

  const renderHeader = () => {
    const user = authStore.getUser();
    const isAuthenticated = authStore.isAuthenticated();

    return (
      <Header className="">
        <img src={logo} alt="Dorémix" class="h-8" />
        <div class="flex gap-2 items-center">
          {isAuthenticated ? (
            <>
              <span class="text-sm text-gray-300">Hello, {user?.username}</span>
              <Button variant="outline" size="sm" id="logout-btn">Logout</Button>
            </>
          ) : (
            <>
              <Button variant="outline" size="sm" id="login-btn">Login</Button>
              <Button variant="primary" size="sm" id="signup-btn">Signup</Button>
            </>
          )}
        </div>
      </Header>
    );
  };

  // First, render the HTML to the DOM
  const appHtml = (
    <div class="min-h-screen bg-background text-foreground px-6">
      {renderHeader()}

      <main class="" id="mainContent"></main>

      <div id="youtubePlayer"></div>
      <div id="trackPlayerContainer">{TrackPlayer()}</div>
    </div>
  );

  root.innerHTML = appHtml;
  const mainContent = document.getElementById("mainContent");

  // Attach event handlers for auth buttons
  const loginBtn = document.getElementById('login-btn');
  const signupBtn = document.getElementById('signup-btn');
  const logoutBtn = document.getElementById('logout-btn');

  loginBtn?.addEventListener('click', () => router.navigate('/login'));
  signupBtn?.addEventListener('click', () => router.navigate('/signup'));
  logoutBtn?.addEventListener('click', () => {
    authStore.logout();
    router.navigate('/login');
  });

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

  // Subscribe to auth changes to re-render header
  authStore.subscribe(() => {
    const headerContainer = root.querySelector('header')?.parentElement;
    if (headerContainer) {
      const oldHeader = headerContainer.querySelector('header');
      if (oldHeader) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = renderHeader();
        const newHeader = tempDiv.firstElementChild;
        if (newHeader) {
          oldHeader.replaceWith(newHeader);

          // Re-attach event handlers
          const loginBtn = document.getElementById('login-btn');
          const signupBtn = document.getElementById('signup-btn');
          const logoutBtn = document.getElementById('logout-btn');

          loginBtn?.addEventListener('click', () => router.navigate('/login'));
          signupBtn?.addEventListener('click', () => router.navigate('/signup'));
          logoutBtn?.addEventListener('click', () => {
            authStore.logout();
            router.navigate('/login');
          });
        }
      }
    }
  });

  return { mainContent, trackPlayer };
}
