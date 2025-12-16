import {
  createButton,
  createCard,
  createText,
  createHeader,
  createFooter,
} from "../components/index";

export default function init() {
  const root = document.getElementById("app") || document.body;
  root.innerHTML = "";

  // App wrapper
  const appWrapper = document.createElement("div");
  appWrapper.className = "min-h-screen bg-background text-foreground px-6";

  // Header
  const header = createHeader({ header: {} });
  const title = createText({
    className: "font-bold text",
    textContent: "Dorémix",
  });

  header.appendChild(title);

  const rowButtons = document.createElement("div");
  rowButtons.className = "flex gap-2";

  const signBtn = createButton({
    textContent: "Login",
    variant: "ghost",
    size: "sm",
  });
  const signupBtn = createButton({
    textContent: "Signup",
    variant: "destructive",
    size: "sm",
  });
  rowButtons.appendChild(signBtn);
  rowButtons.appendChild(signupBtn);

  header.appendChild(rowButtons);
  appWrapper.appendChild(header);

  const imgUrl1 = new URL("../assets/images/playlist1.jpg", import.meta.url)
    .href;
  const imgUrl2 = new URL("../assets/images/playlist2.jpg", import.meta.url)
    .href;
  const imgUrl3 = new URL("../assets/images/playlist3.jpg", import.meta.url)
    .href;

  const svg1 = new URL("../assets/icons/play.svg", import.meta.url).href;

  const track1 = createCard({
    title: "Hip hop 90s",
    image: imgUrl1,
    content:
      "Golden-era beats, raw flows, and timeless classics from the East Coast to the West Coast.",
    icon: svg1,
    className: "px-0! max-w-[300px] shrink-0",
  });

  const track2 = createCard({
    title: "Classic dubstep",
    image: imgUrl2,
    content:
      "Heavy basslines, dark atmospheres, and the iconic sound that started the movement.",
    icon: svg1,
    className: "px-0! max-w-[300px] shrink-0",
  });

  const track3 = createCard({
    title: "Chill Electro Vibes",
    image: imgUrl3,
    content:
      "Smooth synths, soft beats, and dreamy electronic textures for deep focus and late-night energy.",
    icon: svg1,
    className: "px-0! max-w-[300px] shrink-0",
  });

  const track4 = createCard({
    title: "Hip hop 90s",
    image: imgUrl1,
    content:
      "Golden-era beats, raw flows, and timeless classics from the East Coast to the West Coast.",
    icon: svg1,
    className: "px-0! max-w-[300px] shrink-0",
  });

  const track5 = createCard({
    title: "Classic dubstep",
    image: imgUrl2,
    content:
      "Heavy basslines, dark atmospheres, and the iconic sound that started the movement.",
    icon: svg1,
    className: "px-0! max-w-[300px] shrink-0",
  });

  const track6 = createCard({
    title: "Chill Electro Vibes",
    image: imgUrl3,
    content:
      "Smooth synths, soft beats, and dreamy electronic textures for deep focus and late-night energy.",
    icon: svg1,
    className: "px-0! max-w-[300px] shrink-0",
  });

  const track7 = createCard({
    title: "Chill Electro Vibes",
    image: imgUrl3,
    content:
      "Smooth synths, soft beats, and dreamy electronic textures for deep focus and late-night energy.",
    icon: svg1,
    className: "px-0! max-w-[300px] shrink-0",
  });

  const track8 = createCard({
    title: "Chill Electro Vibes",
    image: imgUrl3,
    content:
      "Smooth synths, soft beats, and dreamy electronic textures for deep focus and late-night energy.",
    icon: svg1,
    className: "px-0! max-w-[300px] shrink-0",
  });

  const tracksCard = createCard({
    title: "Top Tracks",
  });

  const tracksContentCard = createCard({
    className: "flex p-0! gap-10 mt-4 mb-2 overflow-scroll",
  });

  tracksContentCard.appendChild(track1);
  tracksContentCard.appendChild(track2);
  tracksContentCard.appendChild(track3);
  tracksContentCard.appendChild(track4);
  tracksContentCard.appendChild(track5);
  tracksContentCard.appendChild(track6);
  tracksContentCard.appendChild(track7);
  tracksContentCard.appendChild(track8);

  tracksCard.appendChild(tracksContentCard);

  appWrapper.appendChild(tracksCard);

  // Append footer
  appWrapper.appendChild(createFooter());

  // Append app to root
  root.appendChild(appWrapper);
}

init();
