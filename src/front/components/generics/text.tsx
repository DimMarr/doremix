export interface TextProps {
  children?: JSX.Element;
  disabled?: boolean;
  className?: string;
  id?: string;
  [key: string]: any;
}

export function Text({
  disabled = false,
  className = '',
  children,
  ...rest
}: TextProps) {
  const textClass = `${className} ${disabled ? 'disabled' : ''}`;

  return (
    <p class={textClass} {...rest}>
      {children}
    </p>
  );
}
