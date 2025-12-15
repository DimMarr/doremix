export interface HeaderProps {
  className: string;
  disabled: boolean;
}

export function createHeader(props: HeaderProps): HTMLElement {
  const header = document.createElement('header');
  const { disabled, className, ...rest } = props;

  header.className = className + ` flex justify-between items-center gap-2 py-4`;
  if(disabled) header.classList.add('disabled');
  
  Object.assign(header, rest);

  return header;
}

// Type for React usage
export type ButtonComponent = HeaderProps;
