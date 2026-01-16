export class Genre {
    public idGenre: number;
    public label: string;

    constructor(data: Partial<Genre>) {
        Object.assign(this, data);
    }
}
