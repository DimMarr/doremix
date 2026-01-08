import { createPauseIcon } from '../components/generics/pause-icon';
import { createPlayIcon } from '../components/generics/play-icon';
import Playlist from '../models/playlist';
import { Track } from '../models/track';

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
    youtubePlayerHtmlElement: HTMLElement;
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
        { youtubePlayerHtmlElement, playlist }: YoutubePlayerProps,
    ) {
        this.playlist = playlist;
        this.tracks = this.playlist.tracks;
        if (this.tracks.length === 0) {
            throw new Error("Tracks list cannot be empty");
        }


        // Initialise le player youtube avec le player.
        console.log("Creating YT.Player with element:", youtubePlayerHtmlElement);
        console.log("Element in document:", document.body.contains(youtubePlayerHtmlElement));

        this.audioPlayer = new window.YT.Player(youtubePlayerHtmlElement, {
            height: "1",
            width: "1",
            videoId: getVideoId(this.tracks[0]?.youtubeLink ?? ""),
            playerVars: {
                playsinline: 1,
                controls: 0,
                autoplay: 0,
            },
            events: {
                onReady: (event: any) => {
                    console.log("YouTube player is ready!");
                    console.log("onReady event:", event);
                    console.log("onReady event.target:", event.target);
                    console.log("this.audioPlayer:", this.audioPlayer);
                    console.log("Are they the same?", event.target === this.audioPlayer);
                    console.log("audioPlayer iframe:", this.audioPlayer.getIframe?.());
                    this.isPlayerReady = true;
                    // Execute any pending action that was queued before player was ready
                    if (this.pendingAction) {
                        console.log("Executing pending action");
                        this.pendingAction();
                        this.pendingAction = null;
                    }
                },
                onStateChange: (event: { data: number }): void => {
                    console.log("YouTube player state changed:", event.data);
                    // Quand le track se termine on passe au praochine track automatiquement
                    if (event.data === window.YT.PlayerState.ENDED) {
                        this.nextTrack();
                    }
                },
                onError: (event: any) => {
                    console.error("YouTube player error:", event.data);
                    // Error codes: 2=invalid param, 5=HTML5 error, 100=not found, 101/150=not embeddable
                    const errorMessages: Record<number, string> = {
                        2: "Invalid video ID",
                        5: "HTML5 player error",
                        100: "Video not found",
                        101: "Video cannot be embedded",
                        150: "Video cannot be embedded (copyright restriction)",
                    };
                    const message = errorMessages[event.data] || `Unknown error (${event.data})`;
                    console.error("YouTube error:", message);

                    // Update UI to show error
                    const currentTrackDisplay = document.getElementById("currentTrack");
                    if (currentTrackDisplay) {
                        currentTrackDisplay.textContent = `⚠️ ${message}`;
                    }
                },
            },
        });

        console.log("YT.Player created, audioPlayer:", this.audioPlayer);

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

    private setTimer(): void {
        const trackTimerId = "trackTimer";
        const trackTimer = document.getElementById(trackTimerId) as
            | HTMLInputElement
            | null;
        const trackElapsedTime = document.getElementById("trackElapsedTime") as HTMLSpanElement | null;
        const trackTotalTime = document.getElementById("trackTotalTime") as HTMLSpanElement | null;

        if (!trackTimer || !trackElapsedTime || !trackTotalTime) {
            console.error(`Some track elements with IDs ${trackTimerId}, trackElapsedTime or trackTotalTime were not found.`);
            return;
        }

        if (!trackTimer.value) {
            trackTimer.value = "0";
        }
        trackTimer.min = "0";
        trackTimer.max = String(this.audioPlayer.getDuration());


        const duration = this.audioPlayer.getDuration() || 0;
        trackTotalTime.textContent = new Date(duration * 1000).toISOString().substr(14, 5);

        if (this.intervalChangeVideo) {
            clearInterval(this.intervalChangeVideo);
        }

        this.intervalChangeVideo = setInterval(() => {
            trackTimer.max = String(this.audioPlayer.getDuration());
            const currentTime = this.audioPlayer.getCurrentTime() || 0;
            trackElapsedTime.textContent = new Date(currentTime * 1000).toISOString().substr(14, 5);
            const currentVideoTime = this.audioPlayer.getCurrentTime();
            this.updateTimer(currentVideoTime);
        }, 32);
    }

    // Audio controls
    changeTrackState(): void {
        // Don't do anything if player isn't ready yet
        if (!this.isPlayerReady) {
            console.log("changeTrackState: Player not ready yet");
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
        console.log("playVideo called");
        console.log("isPlayerReady:", this.isPlayerReady);
        console.log("audioPlayer exists:", !!this.audioPlayer);
        console.log("audioPlayer.playVideo exists:", !!this.audioPlayer?.playVideo);

        if (!this.isPlayerReady) {
            console.warn("playVideo called but player is not ready yet");
            return;
        }

        if (this.audioPlayer && this.audioPlayer.playVideo) {
            console.log("Calling audioPlayer.playVideo()");

            const playBtn = document.querySelector("#playBtn");
            console.log("playBtn found:", playBtn);

            if (playBtn) {
                playBtn.innerHTML = "";
                playBtn.appendChild(createPauseIcon());
            }

            this.audioPlayer.playVideo();
            console.log("playVideo executed");
        } else {
            console.error("Cannot play - audioPlayer or playVideo missing");
        }
        setTimeout(() => {
            console.log("Player state after playVideo:", this.audioPlayer.getPlayerState());
        }, 1000);
    }

    pauseVideo(): void {
        if (this.audioPlayer && this.audioPlayer.pauseVideo) {
            document.querySelector("#playBtn").innerHTML = "";
            document.querySelector("#playBtn").appendChild(createPlayIcon());
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
        console.log("playTrack called with index:", index);
        console.log("isPlayerReady:", this.isPlayerReady);

        // Re-enable next/prev buttons (playlist context exists)
        const nextBtn = document.getElementById("nextBtn");
        const prevBtn = document.getElementById("previousBtn");
        console.log("Re-enabling buttons:", { nextBtn, prevBtn });
        if (nextBtn) nextBtn.removeAttribute("disabled");
        if (prevBtn) prevBtn.removeAttribute("disabled");

        // Validate index
        if (index < 0 || index >= this.tracks.length) {
            console.warn(`Invalid track index: ${index}`);
            return;
        }

        const track = this.tracks[index];
        console.log("Track to play:", track);

        // Update UI - remove playing state from previous track
        if (this.currentPlayingTrackIndex >= 0) {
            const prevTrackEl = document.getElementById(
                `track-${this.currentPlayingTrackIndex}`,
            );
            if (prevTrackEl) {
                prevTrackEl.classList.remove("playing");
            }
        }

        // Add playing state to current track
        const currentTrackEl = document.getElementById(`track-${index}`);
        if (currentTrackEl) {
            currentTrackEl.classList.add("playing");
        }

        this.currentPlayingTrackIndex = index;

        // Update player display
        const currentTrackDisplay = document.getElementById("currentTrack");
        console.log("currentTrackDisplay found:", currentTrackDisplay);
        if (currentTrackDisplay) {
            currentTrackDisplay.textContent = track.title;
        }

        const playerContainer = document.getElementById("playerContainer");
        console.log("playerContainer found:", playerContainer);
        if (playerContainer) {
            playerContainer.classList.remove("hidden");
            playerContainer.classList.add("flex");
        }

        // Load and play video using YT.Player
        console.log("About to load video, audioPlayer exists:", !!this.audioPlayer);
        console.log("track.youtubeLink:", track.youtubeLink);

        const loadAndPlay = () => {
            if (this.audioPlayer && this.audioPlayer.loadVideoById) {
                const videoId = getVideoId(track.youtubeLink);
                console.log("Extracted videoId:", videoId);
                console.log("audioPlayer before loadVideoById:", this.audioPlayer);
                console.log("audioPlayer.getIframe():", this.audioPlayer.getIframe?.());
                console.log("iframe in document:", this.audioPlayer.getIframe ? document.body.contains(this.audioPlayer.getIframe()) : "no getIframe");
                this.audioPlayer.loadVideoById(videoId);
                console.log("loadVideoById called, now calling playVideo");
                this.playVideo();
            } else {
                console.error("audioPlayer or loadVideoById not available!");
            }

            setTimeout(() => {
                console.log("Setting timer");
                console.log("Player state in timer:", this.audioPlayer.getPlayerState());
                this.setTimer();
            }, 2000);
        };

        // If player is ready, play immediately. Otherwise, queue the action.
        if (this.isPlayerReady) {
            loadAndPlay();
        } else {
            console.log("Player not ready, queuing playTrack action");
            this.pendingAction = loadAndPlay;
        }
    }

    public playSingleTrack(track: Track): void {
        console.log("playSingleTrack called with track:", track);
        console.log("isPlayerReady:", this.isPlayerReady);

        // Clear playing state from previous track (if any)
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

        // Disable next/prev buttons (no playlist context)
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
            // Load and play video (same as playTrack)
            if (this.audioPlayer && this.audioPlayer.loadVideoById) {
                const videoId = getVideoId(track.youtubeLink || "");
                console.log("playSingleTrack - Extracted videoId:", videoId);
                this.audioPlayer.loadVideoById(videoId);
                this.playVideo();
            }

            // Set timer (same as playTrack)
            setTimeout(() => {
                this.setTimer();
            }, 2000);
        };

        // If player is ready, play immediately. Otherwise, queue the action.
        if (this.isPlayerReady) {
            loadAndPlay();
        } else {
            console.log("Player not ready, queuing playSingleTrack action");
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
    destroy(): void {
        if (this.intervalChangeVideo) {
            clearInterval(this.intervalChangeVideo);
            this.intervalChangeVideo = null;
        }
    }

    // Player GETTERS state
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
}

export default YoutubePlayer;
export type { YTPlayer };
