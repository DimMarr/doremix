import {
  createButton,
  createCard,
  createText,
  createHeader,
  createFooter
} from '../components/generics/index';
import { createTrackPlayer } from '../components/playlists';
import { createTrackPlayerContainer } from '../components/playlists/track-player';
import PlaylistRepository from '../repositories/playlistRepository';
import YoutubePlayer from '../store/track-player';
import { waitForYouTubeAPI } from '../utils/youtube-api-loader';

export default function init() {

  const root = document.getElementById('app') || document.body;
  root.innerHTML = '';

  // App wrapper
  const appWrapper = document.createElement('div');
  appWrapper.className = 'min-h-screen bg-background text-foreground px-6';

  // Header
  const header = createHeader({ header: {} });
  const title = createText({ className: 'font-bold text', textContent: 'Dorémix' });

  header.appendChild(title);

  const rowButtons = document.createElement('div');
  rowButtons.className = 'flex gap-2';

  const signBtn = createButton({ textContent: 'Login', variant: 'ghost', size: 'sm' });
  const signupBtn = createButton({ textContent: 'Signup', variant: 'destructive', size: 'sm' });
  rowButtons.appendChild(signBtn);
  rowButtons.appendChild(signupBtn);

  header.appendChild(rowButtons);
  appWrapper.appendChild(header);

  const svg1 = new URL('../assets/icons/play.svg', import.meta.url).href;

  const tracksCard = createCard({
    title: 'Top Tracks',
  });

  const tracksContentCard = createCard({
    className: "flex p-0! gap-10 mt-4 mb-2 overflow-scroll"
  })

  const trackPlayerContainer = createTrackPlayerContainer()
  appWrapper.appendChild(trackPlayerContainer);

  // Récupérations des playlists
  const repo = new PlaylistRepository();
  const playlists = repo.getPlaylists();

  let trackPlayer = undefined;

  waitForYouTubeAPI().then(() => {
    trackPlayer = new YoutubePlayer({
      playlist: playlists[0],
      youtubePlayerHtmlElement: trackPlayerContainer
    });

    const playerUI = createTrackPlayer({
      youtubePlayer: trackPlayer,
      trackPlayerElement: trackPlayerContainer
    });
    appWrapper.appendChild(playerUI);
  });

  // On créeer dynamiquement les cards pour chaque playlist
  playlists.forEach((p) => {
    const card = createCard({
      title: p.name || '',
      image: p.image,
      content: p.description || '',
      icon: svg1,
      className: 'px-0! max-w-[300px] shrink-0',
      // Lorsqu'on clique sur le bouton play d'une playlist on doit jouer la playlist.
      onClickPlay: () => {
        trackPlayer.setPlaylist(p);
        trackPlayer.playTrack(0);
      }
    });
    tracksContentCard.appendChild(card);
  });

  tracksCard.appendChild(tracksContentCard);


  appWrapper.appendChild(tracksCard);

  // Append trackplayer and keep a reference for play control


  // Append app to root
  root.appendChild(appWrapper);
}

init();