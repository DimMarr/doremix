/**
 * Merge and combine class names, removing duplicates and handling conditions
 * Similar to clsx but lightweight and focused on Tailwind
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ').replace(/\s+/g, ' ').trim();
}

/**
 * Type for button variants matching shadcn style
 */
export type ButtonVariant = 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
export type ButtonSize = 'sm' | 'md' | 'lg' | 'icon';

/**
 * Get button styles based on variant and size
 */
export function getButtonClasses(variant: ButtonVariant = 'default', size: ButtonSize = 'md'): string {
  const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses: Record<ButtonVariant, string> = {
    default: 'bg-primary text-primary-foreground hover:bg-primary/90',
    destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    link: 'text-primary underline-offset-4 hover:underline',
  };

  const sizeClasses: Record<ButtonSize, string> = {
    sm: 'h-8 px-3 text-xs',
    md: 'h-10 px-4 py-2 text-sm',
    lg: 'h-12 px-8 text-base',
    icon: 'h-10 w-10',
  };

  return cn(baseClasses, variantClasses[variant], sizeClasses[size]);
}

export function getInputClasses(): string {
  return cn(
    'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
  );
}

export function getCardClasses(): string {
  return 'rounded-lg bg-[#161616] p-5';
}

export type BadgeVariant = 'default' | 'secondary' | 'destructive' | 'outline';

export function getBadgeClasses(variant: BadgeVariant = 'default'): string {
  const baseClasses = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2';

  const variantClasses: Record<BadgeVariant, string> = {
    default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
    secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
    destructive: 'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
    outline: 'text-foreground border border-foreground/25',
  };

  return cn(baseClasses, variantClasses[variant]);
}

export function getDialogOverlayClasses(): string {
  return 'fixed inset-0 z-50 bg-black/50 backdrop-blur-sm transition-opacity duration-200';
}

export function getDialogContentClasses(): string {
  return 'fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border border-[hsl(var(--border))] bg-background p-6 shadow-lg duration-200 rounded-lg';
}

export function secondsToReadableTime(seconds: number): string {
  if (isNaN(seconds) || seconds === null || seconds === undefined) {
    return '∞';
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  const formattedMinutes = String(minutes).padStart(1, '0');
  const formattedSeconds = String(remainingSeconds).padStart(2, '0');

  return `${formattedMinutes}:${formattedSeconds}`;
}
