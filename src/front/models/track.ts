import { Artist } from "@models/artist";

export class Track {
    public idTrack?: number;
    public title?: string;
    public youtubeLink?: string;
    public listeningCount?: number;
    public durationSeconds?: number;
    public createdAt?: string;
    public artists?: Artist[];

    constructor(data: Partial<Track>) {
        Object.assign(this, data);
    }
}
