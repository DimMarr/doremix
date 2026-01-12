import { Track } from "@models/track";

export default class Playlist {
    public idPlaylist?: number;
    private idOwner?: number;
    public name?: string;
    private idGenre?: number;
    public createdAt?: string;
    public updatedAt?: string;
    public vote?: number;
    public visibility: Visibility = Visibility.public;
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
    shared = "shared",
}
