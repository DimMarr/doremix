import { cn, BadgeVariant, getBadgeClasses } from '../utils';

export interface BadgeProps {
  variant?: BadgeVariant;
  text: string;
  className: string;
}

/**
 * Create badge HTML element
 */
export function createBadge(props: BadgeProps): HTMLSpanElement {
  const badge = document.createElement('span');
  const { variant = 'default', className, text, ...rest } = props;

  badge.className = cn(getBadgeClasses(variant), className);
  badge.textContent = text ?? '';

  Object.assign(badge, rest);

  return badge;
}

// Type for React usage
export type BadgeComponent = BadgeProps;
