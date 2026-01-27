import { cn, getCardClasses } from '@components/index';
import { trackPlayerInstance } from '@layouts/mainLayout';
import Playlist from '@models/playlist';

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
  [key: string]: any;
}

export function Card({
  image,
  title,
  content,
  icon,
  className = '',
  onClickPlay,
  href,
  children,
  ...rest
}: CardProps) {
  const cardClasses = cn(getCardClasses(), className);

  const cardContent = (
    <div class="flex flex-col space-y-1.5 relative lg:min-w-[250px] min-w-[200px]">
      {image as 'safe' && (
        <div class="relative mb-6">
          <img
            safe
            src={image}
            alt={title || 'Card image'}
            class="w-[200px]! h-[200px]! md:h-[250px]! md:w-[300px]! w-auto object-cover object-center rounded-md"
          />
          {icon as 'safe' && (
            <img
              safe
              src={icon}
              alt="Play icon"
              class="absolute bottom-2 right-2 w-[40px] h-[40px] bg-primary p-2 rounded-[999px] cursor-pointer"
              onclick={`(e) => { e.preventDefault(); e.stopPropagation(); ${onClickPlay?.toString() || ''} }`}
            />
          )}
        </div>
      )}

      {title as 'safe' && (
        <h2 safe class="text-lg font-semibold leading-none tracking-tight">
          {title}
        </h2>
      )}

      {content as 'safe' && (
        <p safe class="text-sm text-muted-foreground">{content}</p>
      )}

      {children}
    </div>
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

export function buildCardsFromPlaylists(playlists: Playlist[]){
  const svg1 = new URL("../../assets/icons/play.svg", import.meta.url).href;

  return playlists.map((p) => {
    const cardHtml = Card({
      title: p.name || "",
      image: p.image,
      content: p.description || "",
      icon: svg1,
      className: "px-0! max-w-[200px] md:max-w-[300px] shrink-0",
      onClickPlay: () => {
        if (trackPlayerInstance.playlist.idPlaylist !== p.idPlaylist) {
          trackPlayerInstance.setPlaylist(p);
        }
        trackPlayerInstance.playTrack(0);
      },
    });

    return `<a href="/playlist/${p.idPlaylist}" data-link>${cardHtml}</a>`;
  }).join('');

}

export function initCardsElements(container: HTMLElement, playlists: Playlist[]){
  const cardElements = container.querySelectorAll('[data-link]');
  cardElements.forEach((link, index) => {
    const p = playlists[index];
    const iconElement = link.querySelector('img[alt="Play icon"]');
    if (iconElement) {
      iconElement.addEventListener('click', (e) => {
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
