import { cn, ButtonVariant, ButtonSize, getButtonClasses } from '@components/index';

export interface ButtonProps {
  className?: string;
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  disabled?: boolean;
  children?: JSX.Element;
  id?: string;
  title?: string;
  [key: string]: any;
}

export function Button({
  className,
  variant = 'default',
  size = 'md',
  loading = false,
  disabled = false,
  children,
  ...rest
}: ButtonProps) {
  const baseClass = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium  focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-white/50 transition-colors disabled:pointer-events-none disabled:opacity-50 px-4 py-2 cursor-pointer";

  const buttonClass = cn(baseClass, getButtonClasses(variant, size), className);
  const isDisabled = disabled || loading;

  return (
    <button
      class={buttonClass}
      disabled={isDisabled}
      {...rest}
    >
      {children}
    </button>
  );
}
