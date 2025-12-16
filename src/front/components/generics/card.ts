import { cn, getCardClasses } from "../utils";

export interface CardProps {
  image: string;
  icon: string;
  title?: string;
  content?: string;
  className: string;
  onClickPlay?: () => void;
}

export function createCard(props: CardProps): HTMLDivElement {
  const { image, title, content, icon, className, onClickPlay, ...rest } = props;

  const card = document.createElement("div");
  card.className = cn(getCardClasses(), className);

  const headerDiv = document.createElement("div");
  headerDiv.className = "flex flex-col space-y-1.5 relative";

  if (image) {
    const container = document.createElement("div");
    container.className = "relative mb-6";
    const imageElement = document.createElement("img");
    imageElement.src = image;
    imageElement.className =
      " w-[200px]! h-[200px]! md:h-[250px]! md:w-[300px]! w-auto object-cover object-center rounded-md";

    if (icon) {
      const iconElement = document.createElement("img");
      iconElement.src = icon;
      iconElement.className =
        "absolute bottom-2 right-2 w-[40px] w-[40px] bg-[#2b7fff] p-2 rounded-[999px] cursor-pointer";
      if (onClickPlay) {
        iconElement.addEventListener("click", (e) => {
          e.stopPropagation();
          onClickPlay();
        });
      }
      container.appendChild(iconElement);
    }

    container.appendChild(imageElement);
    headerDiv.appendChild(container);
  }

  if (title) {
    const titleEl = document.createElement("h2");
    titleEl.className = "text-lg font-semibold leading-none tracking-tight";
    titleEl.textContent = title;
    headerDiv.appendChild(titleEl);
  }
  if (content) {
    const descEl = document.createElement("p");
    descEl.className = "text-sm text-muted-foreground";
    descEl.textContent = content;
    headerDiv.appendChild(descEl);
  }

  if(headerDiv.children.length){
    card.appendChild(headerDiv);    
  }

  Object.assign(card, rest);
  return card;
}

// Types for React usage
export type CardComponent = CardProps;
