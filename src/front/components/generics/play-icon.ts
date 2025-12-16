

export function createPlayIcon() {
    const iconElement = document.createElement("img");
    iconElement.src = "/assets/icons/play.svg";
    iconElement.className   = "absolute z-[99] w-[40px] w-[40px] p-2 rounded-[999px] cursor-pointer";
    return iconElement;
}
