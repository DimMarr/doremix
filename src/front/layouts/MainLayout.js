import { createButton, createHeader, createText } from "../components/generics";
import {
  createTrackPlayer,
  createTrackPlayerContainer,
} from "../components/playlists/track-player";
import PlaylistRepository from "../repositories/playlistRepository";
import YoutubePlayer from "../store/track-player";
import { waitForYouTubeAPI } from "../utils/youtube-api-loader";

export async function createMainLayout() {
  const root = document.getElementById("app") || document.body;
  root.innerHTML = "";

  // App wrapper
  const appWrapper = document.createElement("div");
  appWrapper.className = "min-h-screen bg-background text-foreground px-6";

  // Header
  const header = createHeader({ header: {} });
  const logo = document.createElement("img");
  logo.src = "/assets/images/logo.png";
  logo.alt = "Dorémix";
  logo.className = "h-8";
  header.appendChild(logo);

  const rowButtons = document.createElement("div");
  rowButtons.className = "flex gap-2";
  const signBtn = createButton({
    textContent: "Login",
    variant: "ghost",
    size: "sm",
  });
  const signupBtn = createButton({
    textContent: "Signup",
    variant: "destructive",
    size: "sm",
  });
  rowButtons.appendChild(signBtn);
  rowButtons.appendChild(signupBtn);
  header.appendChild(rowButtons);
  appWrapper.appendChild(header);

  const mainContent = document.createElement("main");
  mainContent.className = "";
  appWrapper.appendChild(mainContent);

  const trackPlayerContainer = createTrackPlayerContainer();
  appWrapper.appendChild(trackPlayerContainer);

  root.appendChild(appWrapper);

  // This is problematic, we need playlists for the youtube player
  // I'll just use the first one for now.
  const repo = new PlaylistRepository();
  const playlists = await repo.getPlaylists();

  await waitForYouTubeAPI();

  const trackPlayer = new YoutubePlayer({
    playlist: playlists[0],
    youtubePlayerHtmlElement: trackPlayerContainer,
  });
  const playerUI = createTrackPlayer({
    youtubePlayer: trackPlayer,
    trackPlayerElement: trackPlayerContainer,
  });
  appWrapper.appendChild(playerUI);

  return { mainContent, trackPlayer };
}
