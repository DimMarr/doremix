import { ArtistRepository } from "@repositories/artistRepository";
import { AppRoutes } from "../router";
import { Artist } from "@models/artist";

export async function ArtistsPage(
  container: HTMLElement | null,
  onNavigate: (path: string) => void
) {
  if (!container) return;

  const repo = new ArtistRepository();
  let artists: Artist[] = [];
  try {
    artists = await repo.getAll();
  } catch (error) {
    console.error("Failed to load artists", error);
  }

  container.innerHTML = (
    <div class="py-8">
      <h1 class="text-3xl font-bold mb-6">Artists</h1>

      <div class="mb-8">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35" />
          </svg>
          <input
            id="artist-search-input"
            type="text"
            placeholder="Rechercher un artiste..."
            class="w-full pl-9 pr-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-500/40 focus:border-blue-500/40 transition-all"
          />
        </div>
      </div>

      <div id="artists-list-container" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        {(await Promise.all(artists.map(async (artist) => await (
          <div
            data-artist-id={artist.idArtist}
            class="artist-card flex flex-col items-center gap-4 bg-white/5 p-6 rounded-xl hover:bg-white/10 transition-colors cursor-pointer border border-white/5 hover:border-white/10 group"
          >
            <div class="w-full aspect-square rounded-full bg-neutral-800 flex items-center justify-center text-4xl shadow-lg border border-white/10 group-hover:scale-105 transition-transform duration-300 overflow-hidden">
              {artist.imageUrl ? <img src={artist.imageUrl} alt={artist.name} class="w-full h-full object-cover" /> : '🎵'}
            </div>
            <h3 class="font-semibold text-center truncate w-full" title={artist.name}>
              {artist.name}
            </h3>
          </div>
        )))) as unknown as 'safe'}
      </div>
    </div>
  ) as unknown as string;

  // Search filter
  const searchInput = container.querySelector('#artist-search-input') as HTMLInputElement | null;
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const query = searchInput.value.toLowerCase().trim();
      const trackListContainer = container.querySelector('#artists-list-container');
      if (!trackListContainer) return;

      const rows = trackListContainer.querySelectorAll('.artist-card');
      rows.forEach((row) => {
        const htmlRow = row as HTMLElement;
        const text = htmlRow.textContent?.toLowerCase() ?? '';
        if (!query || text.includes(query)) {
          htmlRow.style.display = '';
        } else {
          htmlRow.style.display = 'none';
        }
      });
    });
  }

  // Event delegation
  container.onclick = (e: MouseEvent) => {
    const target = e.target as HTMLElement;

    const artistCard = target.closest('.artist-card') as HTMLElement | null;
    if (artistCard) {
      const artistId = artistCard.getAttribute('data-artist-id');
      if (artistId) {
        onNavigate(`/artists/${artistId}`);
        return;
      }
    }
  };
}
