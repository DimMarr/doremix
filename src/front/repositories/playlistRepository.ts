import Playlist, { Visibility } from "../models/playlist";
import { Track } from "../models/track";

const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
const img2 = new URL("../assets/images/playlist2.jpg", import.meta.url).href;
const img3 = new URL("../assets/images/playlist3.jpg", import.meta.url).href;

const playlists = [
    new Playlist({
        idPlaylist: 1,
        name: "Hip Hop 90s",
        description:
            "Golden-era beats, raw flows, and timeless classics from the East to the West.",
        image: img1,
        tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up", durationSeconds: 61, artist: {id: 1,name: "Rick Astley"} }), new Track({idTrack: 1, youtubeLink: "RMXJ2PW8rrE", title: "Superhero"})],
        visibility: Visibility.public,
    }),
    new Playlist({
        idPlaylist: 2,
        name: "Classic dubstep",
        description:
            "Heavy basslines, dark atmospheres, and the iconic sound that started it all.",
        image: img2,
        tracks: [new Track({idTrack: 1, youtubeLink: "_WCD3Z9UmJ4", title: "Superhero - Metro boomin, Future"}), new Track({idTrack: 1, youtubeLink: "fCRCLsJQWUQ", title: "IDGAF - Drake, Yeat"}) ],
        visibility: Visibility.public,
    }),
    new Playlist({
        idPlaylist: 3,
        name: "Chill Electro Vibes",
        description:
            "Smooth synths and dreamy textures for focus, study, and late-night energy.",
        image: img3,
        tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
        visibility: Visibility.public,
    }),
    new Playlist({
        idPlaylist: 4,
        name: "Lo‑Fi Study",
        description: "Mellow beats and nostalgic textures to keep you in flow.",
        image: img1,
        tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
        visibility: Visibility.public,
    }),
    new Playlist({
        idPlaylist: 5,
        name: "Future Bass Gems",
        description: "Lush chords, vocal chops, and uplifting drops.",
        image: img2,
        tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
        visibility: Visibility.public,
    }),
    new Playlist({
        idPlaylist: 6,
        name: "Techno Warehouse",
        description: "Driving rhythms and hypnotic grooves from the underground.",
        image: img3,
        tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
        visibility: Visibility.public,
    }),
    new Playlist({
        idPlaylist: 7,
        name: "Soulful House",
        description: "Groovy basslines and warm vocals to move your feet.",
        image: img1,
        tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
        visibility: Visibility.public,
    }),
    new Playlist({
        idPlaylist: 8,
        name: "Indie Chill",
        description: "Laid-back guitars and cozy melodies for relaxed vibes.",
        image: img2,
        tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
        visibility: Visibility.public,
    }),
];

export default class PlaylistRepository {
    getPlaylists(): Playlist[] {
        return playlists;
    }

    getPlaylistById(id: number): Playlist | undefined {
        return playlists.find(p => p.idPlaylist === id);
    }
}
