export interface TextProps {
  children: string;
  disabled: boolean;
  className: string;
}

export function createText(props: TextProps): HTMLElement {
  const text = document.createElement('p');
  const { disabled, className, children, ...rest } = props;

  text.className = className ?? "";
  if(disabled) text.classList.add("disabled");
  text.innerHTML = typeof children === 'string' ? children : '';

  Object.assign(text, rest);

  return text;
}

export type TextComponent = Text;
