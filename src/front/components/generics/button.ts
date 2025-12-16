import { cn, ButtonVariant, ButtonSize, getButtonClasses } from '../utils';

export interface ButtonProps {
  className?: string;
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  disabled?: boolean;
  text?: string;
}

export function createButton(props: ButtonProps): HTMLButtonElement {
  const button = document.createElement('button');
  const { variant = 'default', size = 'md', loading = false, disabled = false, className, text, ...rest } = props;

  const baseClass = "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium bg-neutral-900 text-neutral-100 hover:bg-neutral-800   focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-white/50 transition-colors disabled:pointer-events-none disabled:opacity-50 h-10 px-4 py-2 cursor-pointer";
  button.className = cn(getButtonClasses(variant, size), baseClass);

  if(disabled || loading){
    button.classList.add('disabled');
  }

  button.textContent = text ?? "";
  Object.assign(button, rest);

  return button;
}

// Type for React usage
export type ButtonComponent = ButtonProps;
