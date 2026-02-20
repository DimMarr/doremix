import { Track } from "@models/track";

export default class Playlist {
    public idPlaylist?: number;
    public idOwner?: number;
    public name?: string;
    public idGenre?: number;
    public genreLabel?: string;
    public createdAt?: string;
    public updatedAt?: string;
    public vote?: number;
    public visibility: Visibility = Visibility.private;
    public image?: string;
    public description?: string;
    public tracks: Track[] = [];

    constructor(data: Partial<Playlist>) {
        Object.assign(this, data);
    }
}

export enum Visibility {
    public = "public",
    private = "private",
    open = "open",
}
