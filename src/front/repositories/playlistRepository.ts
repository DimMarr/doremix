

import Playlist, { Visibility } from "../models/playlist";
import { Track } from "../models/track";

export default class PlaylistRepository {
    getPlaylists(): Playlist[] {
        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
        const img2 = new URL("../assets/images/playlist2.jpg", import.meta.url).href;
        const img3 = new URL("../assets/images/playlist3.jpg", import.meta.url).href;

        return [
            new Playlist({
                name: "Hip Hop 90s",
                description:
                    "Golden-era beats, raw flows, and timeless classics from the East to the West.",
                image: img1,
                tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"}), new Track({idTrack: 1, youtubeLink: "RMXJ2PW8rrE", title: "Superhero"})],
                visibility: Visibility.public,
            }),
            new Playlist({
                name: "Classic dubstep",
                description:
                    "Heavy basslines, dark atmospheres, and the iconic sound that started it all.",
                image: img2,
                tracks: [new Track({idTrack: 1, youtubeLink: "_WCD3Z9UmJ4", title: "Superhero - Metro boomin, Future"}), new Track({idTrack: 1, youtubeLink: "fCRCLsJQWUQ", title: "IDGAF - Drake, Yeat"}) ],
                visibility: Visibility.public,
            }),
            new Playlist({
                name: "Chill Electro Vibes",
                description:
                    "Smooth synths and dreamy textures for focus, study, and late-night energy.",
                image: img3,
                tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
                visibility: Visibility.public,
            }),
            new Playlist({
                name: "Lo‑Fi Study",
                description: "Mellow beats and nostalgic textures to keep you in flow.",
                image: img1,
                tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
                visibility: Visibility.public,
            }),
            new Playlist({
                name: "Future Bass Gems",
                description: "Lush chords, vocal chops, and uplifting drops.",
                image: img2,
                tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
                visibility: Visibility.public,
            }),
            new Playlist({
                name: "Techno Warehouse",
                description: "Driving rhythms and hypnotic grooves from the underground.",
                image: img3,
                tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
                visibility: Visibility.public,
            }),
            new Playlist({
                name: "Soulful House",
                description: "Groovy basslines and warm vocals to move your feet.",
                image: img1,
                tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
                visibility: Visibility.public,
            }),
            new Playlist({
                name: "Indie Chill",
                description: "Laid-back guitars and cozy melodies for relaxed vibes.",
                image: img2,
                tracks: [new Track({idTrack: 1, youtubeLink: "dQw4w9WgXcQ", title: "Never Gonna Give You Up"})],
                visibility: Visibility.public,
            }),
        ];
    }
}
