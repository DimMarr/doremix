import { cn, getCardClasses } from '@components/index';

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
    <div class="flex flex-col space-y-1.5 relative min-w-[200px]">
      {image && (
        <div class="relative mb-6">
          <img
            src={image}
            alt={title || 'Card image'}
            class="w-[200px]! h-[200px]! md:h-[250px]! md:w-[300px]! w-auto object-cover object-center rounded-md"
          />
          {icon && (
            <img
              src={icon}
              alt="Play icon"
              class="absolute bottom-2 right-2 w-[40px] h-[40px] bg-[#2b7fff] p-2 rounded-[999px] cursor-pointer"
              onclick={`(e) => { e.preventDefault(); e.stopPropagation(); ${onClickPlay?.toString() || ''} }`}
            />
          )}
        </div>
      )}

      {title && (
        <h2 class="text-lg font-semibold leading-none tracking-tight">
          {title}
        </h2>
      )}

      {content && (
        <p class="text-sm text-muted-foreground">{content}</p>
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
