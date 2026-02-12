import { cn, getCardClasses } from '@components/index';
import { trackPlayerInstance } from '@layouts/mainLayout';
import Playlist, { Visibility } from '@models/playlist';

export interface CardProps {
  image?: string;
  icon?: string;
  title?: string;
  content?: string;
  className?: string;
  onClickPlay?: () => void;
  href?: string;
  children?: JSX.Element;
  id?: string;
  visibility?: Visibility;
  [key: string]: any;
}

const getVisibilityIcon = (visibility?: Visibility) => {
  if (!visibility) return null;

  const iconClass = "w-3.5 h-3.5 text-white/90";
  const containerClass = "absolute top-2 left-2 bg-black/60 backdrop-blur-md p-1.5 rounded-full z-10 shadow-sm border border-white/10";

  switch (visibility.toLowerCase()) {
    case Visibility.private:
      return (
        <div class={containerClass} title="Private Playlist">
          <svg class={iconClass} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0110 0v4" />
          </svg>
        </div>
      );
    case Visibility.public:
      return (
        <div class={containerClass} title="Public Playlist">
          <svg class={iconClass} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <circle cx="12" cy="12" r="10" />
            <path d="M2 12h20" />
            <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
          </svg>
        </div>
      );

    case Visibility.open:
      return (
        <div class={containerClass} title="Open Playlist">
          <svg class={iconClass} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" />
          </svg>
        </div>
      )
    default:
      return null;
  }
};

export function Card({
  image,
  title,
  content,
  icon,
  className = '',
  onClickPlay,
  href,
  children,
  visibility,
  ...rest
}: CardProps) {
  const cardClasses = cn(getCardClasses(), "group relative flex flex-col gap-2 transition-all duration-300 hover:bg-white/10 p-3 rounded-md", className);

  const cardContent = (
    <>
      <div class="relative w-full aspect-square overflow-hidden rounded-md shadow-lg mb-2">
        {getVisibilityIcon(visibility) as 'safe'}

        {image as 'safe' ? (
          <img
            safe
            src={image}
            alt={title || 'Card image'}
            class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div class="w-full h-full bg-neutral-800 flex items-center justify-center text-neutral-500">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2" /><circle cx="9" cy="9" r="2" /><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" /></svg>
          </div>
        )}

        {/* Play Button Overlay */}
        {icon as 'safe' && (
          <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
            <button
              class="transform translate-y-4 group-hover:translate-y-0 transition-transform duration-300 bg-primary text-black rounded-full p-3 shadow-xl hover:scale-105"
              onclick={`(e) => { e.preventDefault(); e.stopPropagation(); ${onClickPlay?.toString() || ''} }`}
            >
              <img src={icon} alt="Play" class="w-6 h-6 ml-0.5" />
            </button>
          </div>
        )}
      </div>

      <div class="flex flex-col gap-0.5 min-w-0">
        {title as 'safe' && (
          <h3 safe class="font-semibold text-white truncate text-base" title={title}>
            {title}
          </h3>
        )}

        {content as 'safe' && (
          <p safe class="text-sm text-neutral-400 truncate" title={content}>
            {content}
          </p>
        )}

        {children}
      </div>
    </>
  );

  if (href) {
    return (
      <a href={href} class={cardClasses} {...rest}>
        {cardContent}
      </a>
    );
  }

  return (
    <div class={cardClasses} {...rest}>
      {cardContent}
    </div>
  );
}

export function buildCardsFromPlaylists(playlists: Playlist[]) {
  const svg1 = new URL("../../assets/icons/play.svg", import.meta.url).href;

  return playlists.map((p) => {
    return Card({
      title: p.name || "Untitled Playlist",
      image: p.image,
      content: p.description || "",
      icon: svg1,
      className: "w-full",
      href: `/playlist/${p.idPlaylist}`,
      "data-link": "",
      visibility: p.visibility,
      // Restore onClickPlay for potential inline handling or reference
      onClickPlay: () => {
        if (trackPlayerInstance.playlist.idPlaylist !== p.idPlaylist) {
          trackPlayerInstance.setPlaylist(p);
        }
        trackPlayerInstance.playTrack(0);
      }
    });
  }).join('');
}

export function initCardsElements(container: HTMLElement, playlists: Playlist[]) {
  const cardElements = container.querySelectorAll('[data-link]');
  cardElements.forEach((link, index) => {
    const p = playlists[index];
    // We now look for the button, I'll add a data attribute to the button in Card to make this robust
    // See Card implementation above (need to ensure I update Card to include data-play-button)
    // Actually, searching for the button inside the link is safer
    const playButton = link.querySelector('button');

    if (playButton) {
      playButton.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (trackPlayerInstance.playlist.idPlaylist !== p.idPlaylist) {
          trackPlayerInstance.setPlaylist(p);
        }
        trackPlayerInstance.playTrack(0);
      });
    }
  });
}
