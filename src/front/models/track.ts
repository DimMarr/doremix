import { Artist } from "@models/artist";

export type TrackStatus = "ok" | "unavailable" ;

export class Track {
    public idTrack?: number;
    public title?: string;
    public youtubeLink?: string;
    public listeningCount?: number;
    public durationSeconds?: number;
    public createdAt?: string;
    public artists?: Artist[];
    public status?: TrackStatus;

    constructor(data: Partial<Track>) {
        Object.assign(this, data);
    }

    isPlayable(): boolean {
        return this.status === "ok" || this.status === undefined;
    }
}
