import type Playlist from "@models/playlist";

export default interface User {
    banned: boolean;
    email: string;
    idUser: number;
    isVerified: boolean;
    playlists: Playlist[];
    role: Role;
    username: string
}

export enum Role {
    ADMIN = "ADMIN",
    MODERATOR = "MODERATOR",
    USER = "USER"
}
