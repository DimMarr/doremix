import { createPauseIcon } from '../components/generics/pause-icon';
import {createPlayIcon } from '../components/generics/play-icon';
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

export class YoutubePlayer {
    public playlist: Playlist;
    private tracks: Track[] = [];
    private currentPlayingTrackIndex: number = 0;
    private intervalChangeVideo: NodeJS.Timeout | null = null;
    private audioPlayer: YTPlayer;

    constructor(
        { youtubePlayerHtmlElement, playlist }: YoutubePlayerProps,
    ) {
        this.playlist = playlist;
        this.tracks = this.playlist.tracks;
        if(this.tracks.length === 0){
            throw new Error("Tracks list cannot be empty");
        }

        // Initialise le player youtube avec le player.
        this.audioPlayer = new window.YT.Player(youtubePlayerHtmlElement, {
            height: "0",
            width: "0",
            videoId: this.tracks[0].youtubeLink,
            playerVars: {
                playsinline: 1,
                controls: 0,
            },
            events: {
                onReady: () => {},
                onStateChange: (event: { data: number }): void => {
                    // Quand le track se termine on passe au praochine track automatiquement
                    if (event.data === window.YT.PlayerState.ENDED) {
                        this.nextTrack();
                    }
                },
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

        if(!trackTimer.value ){
            trackTimer.value = "0";
        }
        trackTimer.min = "0";
        trackTimer.max = String(this.audioPlayer.getDuration());


        trackTotalTime.textContent = new Date(this.audioPlayer.getDuration() * 1000).toISOString().substr(14, 5);

        if (this.intervalChangeVideo) {
            clearInterval(this.intervalChangeVideo);
        }

        this.intervalChangeVideo = setInterval(() => {
            trackTimer.max = String(this.audioPlayer.getDuration());
            trackElapsedTime.textContent = new Date(this.audioPlayer.getCurrentTime() * 1000).toISOString().substr(14, 5);
            const currentVideoTime = this.audioPlayer.getCurrentTime();
            this.updateTimer(currentVideoTime);
        }, 32);
    }

    // Audio controls
    changeTrackState(): void {
        this.setTimer();
        if (this.audioPlayer && this.audioPlayer.getPlayerState) {
            if(this.audioPlayer.getPlayerState() === YoutubePlayerState.UNSTARTED || this.audioPlayer.getPlayerState() === YoutubePlayerState.CUED){
                this.playTrack(this.currentPlayingTrackIndex);
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
        if (this.audioPlayer && this.audioPlayer.playVideo) {
            document.querySelector("#playBtn").innerHTML = "";
            document.querySelector("#playBtn").appendChild(createPauseIcon());
            this.audioPlayer.playVideo();
        }
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
        // Validate index
        if (index < 0 || index >= this.tracks.length) {
            console.warn(`Invalid track index: ${index}`);
            return;
        }

        const track = this.tracks[index];
        console.log(track);

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
        if (currentTrackDisplay) {
            currentTrackDisplay.textContent = track.title;
        }

        const playerContainer = document.getElementById("playerContainer");
        if (playerContainer) {
            playerContainer.classList.remove("hidden");
            playerContainer.classList.add("flex");
        }

        // Load and play video using YT.Player
        if (this.audioPlayer && this.audioPlayer.loadVideoById) {
            this.audioPlayer.loadVideoById(track.youtubeLink);
            this.playVideo();
        }

        setTimeout(() => {
            this.setTimer();
        }
        , 2000);
    }

    setTrackTime(time: number): void {
        if (this.audioPlayer && this.audioPlayer.seekTo) {
            this.audioPlayer.seekTo(time, true);
        }
    }

    setupChangeTrackStateWhenPressingSpacebar(){
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
