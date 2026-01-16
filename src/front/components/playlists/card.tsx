import { cn, getCardClasses } from "@components/index";

export interface CardPlaylistProps {
  image?: string;
  icon?: string;
  title?: string;
  content?: string;
  className?: string;
  onClickPlay?: () => void;
  children?: JSX.Element;
  id?: string;
  [key: string]: any;
}

export function PlaylistCard({
  image,
  title,
  content,
  icon,
  className = '',
  onClickPlay,
  children,
  ...rest
}: CardPlaylistProps) {
  const cardClass = cn(getCardClasses(), className);

  return (
    <div class={cardClass} {...rest}>
      <div class="flex flex-col space-y-1.5 relative">
        {image as 'safe' && (
          <div class="relative mb-6">
            <img
              safe
              src={image}
              alt={title || 'Playlist cover'}
              class="h-[250px]! w-[300px]! w-auto object-cover object-center rounded-md"
            />
            {icon as 'safe' && (
              <img
                safe
                src={icon}
                alt="Play icon"
                class="absolute bottom-2 right-2 w-[40px] h-[40px] bg-[#2b7fff] p-2 rounded-[999px] cursor-pointer"
                onclick={onClickPlay?.toString()}
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
    </div>
  );
}
