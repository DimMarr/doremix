import { Track, Playlist } from '@models/index';

interface YTPlayer {
    loadVideoById(videoId: string): void;
    playVideo(): void;
    pauseVideo(): void;
    stopVideo(): void;
    getPlayerState(): number;
    getDuration(): number;
    getCurrentTime(): number;
    seekTo(time: number, b: boolean): void;
}

interface YoutubePlayerProps {
    playlist: Playlist;
    youtubePlayerHtmlElementId: string;
}

enum YoutubePlayerState {
    UNSTARTED = -1,
    ENDED = 0,
    PLAYING = 1,
    PAUSED = 2,
    BUFFERING = 3,
    CUED = 5,
}

declare global {
    interface Window {
        YT: {
            Player: any;
            PlayerState: {
                PLAYING: number;
                PAUSED: number;
                ENDED: number;
            };
        };
    }
}

const getVideoId = (link: string) => {
    // Si le lien contient "v=", on coupe, sinon on suppose que c'est déjà l'ID
    const videoIdMatch = link.match(/[?&]v=([^&]+)/);
    return videoIdMatch ? videoIdMatch[1] : link;
};

export class YoutubePlayer {
    public playlist: Playlist;
    private tracks: Track[] = [];
    private currentPlayingTrackIndex: number = 0;
    private intervalChangeVideo: NodeJS.Timeout | null = null;
    private audioPlayer: YTPlayer;
    private isPlayerReady: boolean = false;
    private pendingAction: (() => void) | null = null;

    constructor(
        { youtubePlayerHtmlElementId, playlist }: YoutubePlayerProps,
    ) {
        this.playlist = playlist;
        this.tracks = this.playlist.tracks;
        if (this.tracks.length === 0) {
            throw new Error("Tracks list cannot be empty");
        }

        // Initialise le player youtube avec le player.
        this.audioPlayer = new window.YT.Player(youtubePlayerHtmlElementId, {
            height: "0",
            width: "0",
            videoId: getVideoId(this.tracks[0]?.youtubeLink ?? ""),
            playerVars: {
                playsinline: 1,
                controls: 0,
                autoplay: 0,
            },
            events: {
                onReady: () => {
                    this.isPlayerReady = true;
                    if (this.pendingAction) {
                        this.pendingAction();
                        this.pendingAction = null;
                    }
                },
                onStateChange: (event: { data: number }): void => {
                    // Quand le track se termine on passe au praochine track automatiquement
                    if (event.data === window.YT.PlayerState.ENDED) {
                        this.nextTrack();
                    }
                },
                onError: () => { },
            },
        });

        this.setupChangeTrackStateWhenPressingSpacebar();
    }

    public setPlaylist(playlist: Playlist): void {
        this.playlist = playlist;
        this.tracks = this.playlist.tracks;
        this.currentPlayingTrackIndex = 0;
    }

    // Timer controls
    private updateTimer(videoTime: number): void {
        const trackTimer = document.getElementById("trackTimer") as
            | HTMLInputElement
            | null;
        if (trackTimer) {
            trackTimer.value = String(videoTime);
        }
    }

    public setTimer(): void {
        if (!this.isPlayerReady) {
            console.warn('Cannot set timer: Player not ready yet');
            return;
        }
        const trackTimerId = "trackTimer";
        const trackTimer = document.getElementById(trackTimerId) as
            | HTMLInputElement
            | null;
        const trackElapsedTime = document.getElementById("trackElapsedTime") as HTMLSpanElement | null;
        const trackTotalTime = document.getElementById("trackTotalTime") as HTMLSpanElement | null;

        if (!trackTimer || !trackElapsedTime || !trackTotalTime) {
            return;
        }

        if(!trackTimer.value ) trackTimer.value = "0";
        if(!trackTimer.min) trackTimer.min = "0";
        if(!trackTimer.max) trackTimer.max = String(this.audioPlayer.getDuration());

        trackTotalTime.textContent = new Date(this.audioPlayer.getDuration() * 1000).toISOString().substr(14, 5);

        if (this.intervalChangeVideo) {
            clearInterval(this.intervalChangeVideo);
        }

        this.intervalChangeVideo = setInterval(() => {
            trackTimer.max = String(this.audioPlayer.getDuration());
            let time = this.audioPlayer.getCurrentTime();
            if(!time) return;
            trackElapsedTime.textContent = new Date(time * 1000).toISOString().substr(14, 5);
            this.updateTimer(time);
        }, 32);
    }

    // Audio controls
    changeTrackState(): void {
        if (!this.isPlayerReady) {
            console.warn('Player not ready yet');
            return;
        }
        this.setTimer();
        if (this.audioPlayer && this.audioPlayer.getPlayerState) {
            if (this.audioPlayer.getPlayerState() === YoutubePlayerState.UNSTARTED || this.audioPlayer.getPlayerState() === YoutubePlayerState.CUED) {
                // Don't call playTrack if we're in single track mode
                if (this.currentPlayingTrackIndex === -1) {
                    this.playVideo();
                } else {
                    this.playTrack(this.currentPlayingTrackIndex);
                }
            } else if (
                this.audioPlayer.getPlayerState() ===
                YoutubePlayerState.PLAYING
            ) {
                this.pauseVideo();
            } else {
                this.playVideo();
            }
        }
    }

    playVideo(): void {
        if (!this.isPlayerReady) {
            console.warn('Cannot play: Player not ready yet');
            return;
        }
        if (this.audioPlayer && this.audioPlayer.playVideo) {
            document.querySelector("#playBtn").classList.add("hidden");
            document.querySelector("#pauseBtn").classList.remove("hidden");
            this.audioPlayer.playVideo();
        }
    }

    pauseVideo(): void {
        if (!this.isPlayerReady) {
            console.warn('Cannot pause: Player not ready yet');
            return;
        }
        if (this.audioPlayer && this.audioPlayer.pauseVideo) {
            document.querySelector("#pauseBtn").classList.add("hidden");
            document.querySelector("#playBtn").classList.remove("hidden");
            this.audioPlayer.pauseVideo();
        }
    }

    stopVideo(): void {
        if (this.audioPlayer && this.audioPlayer.stopVideo) {
            this.audioPlayer.stopVideo();
        }
    }

    // Tracks control
    previousTrack(): void {
        const newIndex =
            (this.currentPlayingTrackIndex - 1 + this.tracks.length) %
            this.tracks.length;
        this.playTrack(newIndex);
    }

    nextTrack(): void {
        const newIndex = (this.currentPlayingTrackIndex + 1) %
            this.tracks.length;
        this.playTrack(newIndex);
    }

    playTrack(index: number): void {
        if (!this.isPlayerReady) {
            console.warn('Cannot play track: Player not ready yet');
            return;
        }

        // Re-enable next/prev buttons if they were disabled in single track mode
        const nextBtn = document.getElementById("nextBtn");
        const prevBtn = document.getElementById("previousBtn");
        if (nextBtn) nextBtn.removeAttribute("disabled");
        if (prevBtn) prevBtn.removeAttribute("disabled");

        // Validate index
        if (index < 0 || index >= this.tracks.length) {
            return;
        }

        const track = this.tracks[index];


        if (this.currentPlayingTrackIndex >= 0) {
            const prevTrackEl = document.getElementById(
                `track-${this.currentPlayingTrackIndex}`,
            );
            if (prevTrackEl) {
                prevTrackEl.classList.remove("playing");
            }
        }


        const currentTrackEl = document.getElementById(`track-${index}`);
        if (currentTrackEl) {
            currentTrackEl.classList.add("playing");
        }

        this.currentPlayingTrackIndex = index;


        const currentTrackDisplay = document.getElementById("currentTrack");
        if (currentTrackDisplay) {
            currentTrackDisplay.textContent = track.title;
        }

        const playerContainer = document.getElementById("playerContainer");
        if (playerContainer) {
            playerContainer.classList.remove("hidden");
            playerContainer.classList.add("flex");
        }

        const loadAndPlay = () => {
            if (this.audioPlayer && this.audioPlayer.loadVideoById) {
                const videoId = getVideoId(track.youtubeLink);
                this.audioPlayer.loadVideoById(videoId);
                this.playVideo();
            }

            setTimeout(() => {
                this.setTimer();
            }, 2000);
        };

        if (this.isPlayerReady) {
            loadAndPlay();
        } else {
            this.pendingAction = loadAndPlay;
        }
    }

    public playSingleTrack(track: Track): void {
        if (this.currentPlayingTrackIndex >= 0) {
            const prevTrackEl = document.getElementById(
                `track-${this.currentPlayingTrackIndex}`
            );
            if (prevTrackEl) {
                prevTrackEl.classList.remove("playing");
            }
        }

        // Reset track index (no playlist context)
        this.currentPlayingTrackIndex = -1;

        // Disable next/prev buttons
        const nextBtn = document.getElementById("nextBtn");
        const prevBtn = document.getElementById("previousBtn");
        if (nextBtn) nextBtn.setAttribute("disabled", "true");
        if (prevBtn) prevBtn.setAttribute("disabled", "true");

        // Update player display
        const currentTrackDisplay = document.getElementById("currentTrack");
        if (currentTrackDisplay) {
            currentTrackDisplay.textContent = track.title || "Unknown Track";
        }

        const playerContainer = document.getElementById("playerContainer");
        if (playerContainer) {
            playerContainer.classList.remove("hidden");
            playerContainer.classList.add("flex");
        }

        const loadAndPlay = () => {
            if (this.audioPlayer && this.audioPlayer.loadVideoById) {
                const videoId = getVideoId(track.youtubeLink || "");
                this.audioPlayer.loadVideoById(videoId);
                this.playVideo();
            }

            setTimeout(() => {
                this.setTimer();
            }, 2000);
        };

        if (this.isPlayerReady) {
            loadAndPlay();
        } else {
            this.pendingAction = loadAndPlay;
        }
    }

    setTrackTime(time: number): void {
        if (this.audioPlayer && this.audioPlayer.seekTo) {
            this.audioPlayer.seekTo(time, true);
        }
    }

    setupChangeTrackStateWhenPressingSpacebar() {
        document.addEventListener("keydown", (e) => {
            if (e.code === "Space") {
                e.preventDefault();
                this.changeTrackState();
            }
        });
    }

    // Cleanup method to clear interval when destroying the player
    stopTimer(): void {
        if (this.intervalChangeVideo) {
            clearInterval(this.intervalChangeVideo);
            this.intervalChangeVideo = null;
        }
    }

    getPlayerState(): number {
        return this.audioPlayer ? this.audioPlayer.getPlayerState() : -1;
    }

    getPlayer(): YTPlayer | null {
        return this.audioPlayer;
    }

    getDuration(): number {
        return this.audioPlayer ? this.audioPlayer.getDuration() : 0;
    }

    getCurrentTime(): number {
        return this.audioPlayer ? this.audioPlayer.getCurrentTime() : 0;
    }

    getCurrentTrack(): Track | null {
        return this.tracks[this.currentPlayingTrackIndex] || null;
    }
}

export default YoutubePlayer;
export type { YTPlayer };
