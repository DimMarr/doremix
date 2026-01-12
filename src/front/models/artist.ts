
export class Artist {
    public idArtist?: number;
    public name?: string;

    constructor(data: Partial<Artist>) {
        Object.assign(this, data);
    }
}
