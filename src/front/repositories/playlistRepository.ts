import Playlist, { Visibility } from "../models/playlist";
import { Track } from "../models/track";
import { Artist } from "../models/artist";
import { fetchPlaylists, fetchPlaylist, fetchPlaylistTracks } from "../services/api";

export default class PlaylistRepository {
    async getPlaylists(): Promise<Playlist[]> {
      const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;
      try {
        const rawDataPlaylists = await fetchPlaylists();
        const playlistPromises = rawDataPlaylists.map(async (item: any) => {
            const rawDatatracks = await fetchPlaylistTracks(item.idPlaylist);
            const tracks = [];
            for (const data of rawDatatracks) {
                tracks.push(new Track(data));
            }
            return new Playlist({
                ...item,
                image: item.coverImage ?? img1,
                visibility: item.visibility ? item.visibility.toLowerCase() as Visibility : Visibility.public,
                tracks: tracks
            });
        });
        const playlists = await Promise.all(playlistPromises);
        return playlists;
      } catch (error) {
          console.error("Erreur lors de la récupération des playlists", error);
          return [];
      }
    }

    async getPlaylistById(id: number): Promise<Playlist> {
        const rawData = await fetchPlaylist(id);
        const rawDataTracks = await fetchPlaylistTracks(id);
        const tracks = rawDataTracks.map((data: any) => new Track(data));
        const artists = rawDataTracks.map((data: any) => new Artist(data.artist));

        const img1 = new URL("../assets/images/playlist1.jpg", import.meta.url).href;

        return new Playlist({
            ...rawData,
            image: rawData.coverImage ?? img1,
            visibility: rawData.visibility ? rawData.visibility.toLowerCase() as Visibility : Visibility.public,
            tracks: tracks,
            artists: artists
        });
    }
}
