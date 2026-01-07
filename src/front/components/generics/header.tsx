export interface HeaderProps {
  className?: string;
  disabled?: boolean;
  children?: JSX.Element;
  id?: string;
  [key: string]: any;
}

export function Header({
  className = '',
  disabled = false,
  children,
  ...rest
}: HeaderProps) {
  const headerClass = `${className} flex justify-between items-center gap-2 py-4 ${disabled ? 'disabled' : ''}`;

  return (
    <header class={headerClass} {...rest}>
      {children}
    </header>
  );
}
