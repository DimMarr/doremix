import { cn, BadgeVariant, getBadgeClasses } from '@components/index';

export interface BadgeProps {
  variant?: BadgeVariant;
  text: string;
  className?: string;
  id?: string;
  [key: string]: any;
}

export function Badge({ variant = 'default', className = '', text, ...rest }: BadgeProps) {
  const badgeClass = cn(getBadgeClasses(variant), className);

  return (
    <span class={badgeClass} {...rest}>
      {text}
    </span>
  );
}
