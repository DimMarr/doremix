
export class Artist {
    public idArtist?: number;
    public name?: string;
    public imageUrl?: string;

    constructor(data: Partial<Artist>) {
        Object.assign(this, data);
    }
}
