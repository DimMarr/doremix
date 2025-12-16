import YoutubePlayer from "../../store/track-player";

export interface TrackPlayerProps {
    youtubePlayer: YoutubePlayer;
    trackPlayerElement: HTMLDivElement;
}

// Global player store instance
let playerStore: YoutubePlayer | null = null;

export function createTrackPlayerContainer() {
    // Provide an empty container; YouTube IFrame API will inject the iframe
    const container = document.createElement("div");
    container.classList = "hidden";
    // No id required; we'll pass the element reference directly
    return container;
}

function createPlayerTrackerHtmlElementDesktop() {
    return `<div class="fixed bottom-0 left-0 right-0 bg-[#181818] border-t border-[#282828] shadow-2xl backdrop-blur-sm flex items-start md:items-center justify-between md:flex-row flex-col px-6 py-4 hidden" id="playerContainer">
        <div class="flex items-center justify-between w-full md:w-[400px]">
            <img src="/assets/images/playlist1.jpg" class="w-[75px] h-[75px] mr-4 rounded-md hidden md:block" alt="Music Note Icon" />
            <div class="flex-1 min-w-0 w-full">
                <div class="now-playing text-xs font-semibold text-[#2b7fff] uppercase tracking-wider mb-1">
                    Now Playing
                </div>
                <div class="current-track text-lg font-bold text-white truncate text-ellipsis" id="currentTrack">
                    No track selected
                </div>
            </div>
        </div>

        <div class="flex md:flex-col items-center gap-3 w-[520px] max-w-full">
            <!-- Track Info Section -->
            <div class="flex gap-10 md:order-1 order-2">
                            <!-- Controls Section -->
                <div class="flex items-center justify-center gap-3">
                    <button
                        class="control-btn w-10 h-10 rounded-full md:flex items-center justify-center font-bold text-sm shadow-lg hover:shadow-xl hidden"
                        id="previousBtn"
                        title="Previous Track"
                    >
                        <<
                    </button>

                    <button
                        class="control-btn w-12 h-12 rounded-full relative flex items-center justify-center font-bold shadow-lg hover:shadow-xl"
                        id="playBtn"
                        title="Play"
                    >
                        <img src="/assets/icons/play.svg" class="absolute z-99 w-10 p-2 rounded-[999px] cursor-pointer" >
                    </button>


                    <button
                        class="control-btn w-10 h-10 rounded-full md:flex hidden items-center justify-center font-bold text-sm shadow-lg hover:shadow-xl"
                        id="nextBtn"
                        title="Next Track"
                    >
                        >>
                    </button>
                </div>
            </div>

            <!-- Progress Bar -->
            <div class="mb-4 w-full flex gap-4">
                <span id="trackElapsedTime" class="hidden md:block"></span>
                <input
                class="range-input w-full"
                    type="range"
                    id="trackTimer"
                    class="w-full h-1.5"
                    min="0"
                    max="0"
                />
                <span id="trackTotalTime" class="hidden md:block"></span>
            </div>
        </div>
        <div class="hidden xl:block w-[400px]"></div>
    </div>`;
}

export function createTrackPlayer(props: TrackPlayerProps): HTMLDivElement {
    const { youtubePlayer, trackPlayerElement } = props;

    const trackPlayer = document.createElement("div");

    trackPlayer.innerHTML = createPlayerTrackerHtmlElementDesktop()

    // Append container for YouTube player
    trackPlayer.appendChild(trackPlayerElement);

    // Initialize YouTube Player when API is ready
    const initializePlayer = () => {
        playerStore = youtubePlayer;

        // Setup button event listeners
        setupControlButtons();
    };

    // Setup control button event listeners
    const setupControlButtons = () => {
        const playBtn = trackPlayer.querySelector("#playBtn");
        const previousBtn = trackPlayer.querySelector("#previousBtn");
        const nextBtn = trackPlayer.querySelector("#nextBtn");
        const trackTimer = trackPlayer.querySelector("#trackTimer");

        if (!playBtn || !trackTimer) {
            throw new Error("Some buttons not found were not found");
        }

        playBtn.addEventListener(
            "click",
            () => playerStore!.changeTrackState(),
        );

        if (previousBtn) {
            previousBtn.addEventListener(
                "click",
                () => playerStore!.previousTrack(),
            );
        }

        if (nextBtn) {
            nextBtn.addEventListener(
                "click",
                () => playerStore!.nextTrack()
            );
        }

        trackTimer.addEventListener("input", (e: EventTarget) => {
            playerStore?.setTrackTime(e.target.value);
        });
    };

    // Expose minimal control API on the returned element
    Object.assign(trackPlayer, {
        playTrack: (index: number = 0) => playerStore?.playTrack(index),
    });

    // Check if YouTube API is already loaded
    if (window.YT && window.YT.Player) {
        initializePlayer();
    } else {
        // Load YouTube API if not already loaded
        const tag = document.createElement("script");
        tag.src = "https://www.youtube.com/iframe_api";
        const firstScriptTag = document.getElementsByTagName("script")[0];
        firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);

        // YouTube API calls this function when ready
        (window as any).onYouTubeIframeAPIReady = initializePlayer;
    }

    return trackPlayer;
}

// Type for React usage
export type TrackPlayer = TrackPlayerProps;
