import { Button } from "@components/generics/button";
import PlaylistRepository from "@repositories/playlistRepository";

// Le bouton que nous allons exporter pour main.tsx
export function AddPlaylistButton() {
  return Button({
    id: "btn-open-add-playlist",
    variant: "outline",
    children: (
      <div class="flex items-center gap-2">
        <span class="text-xl">+</span>
        <span>Playlist</span>
      </div>
    )
  });
}

export function AddPlaylistModal() {
  return (
    <div id="add-playlist-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm hidden">
      <div class="bg-gray-900 border border-gray-800 p-8 rounded-xl w-full max-w-md shadow-2xl">
        <h2 class="text-2xl font-bold text-white mb-6">Créer une nouvelle playlist</h2>

        <form id="add-playlist-form" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-1">Nom de la playlist</label>
            <input type="text" name="name" id="playlist-name-input" required class="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:ring-2 focus:ring-blue-500 outline-none"/>
          </div>

          <div class="flex justify-end gap-3 mt-8">
            {Button({
              id: 'close-modal',
              variant: 'ghost',
              children: 'Annuler',
              type: 'button'
            })}
            {Button({
              variant: 'primary',
              children: 'Créer la playlist',
              type: 'submit'
            })}
          </div>
        </form>
      </div>
    </div>
  );
}

// Fonction utilitaire pour gérer les événements de la modale
export function setupModalLogic() {
  const modal = document.getElementById("add-playlist-modal");
  const openBtn = document.getElementById("btn-open-add-playlist");
  const closeBtn = document.getElementById("close-modal");
  const form = document.getElementById("add-playlist-form") as HTMLFormElement;

  if (!modal || !openBtn || !closeBtn || !form) return;

  const toggleModal = () => modal.classList.toggle("hidden");

  openBtn.addEventListener("click", toggleModal);
  closeBtn.addEventListener("click", toggleModal);

  // Fermer si on clique à l'extérieur
  modal.addEventListener("click", (e) => {
    if (e.target === modal) toggleModal();
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const name = formData.get("name")?.toString().trim();

    if (!name) {
        alert("Le nom de la playlist est requis");
        return;
    }

    try {
        await PlaylistRepository.createPlaylist(name);
        form.reset();
        toggleModal();
        window.location.reload();
    } catch (err) {
        console.error(err);
        alert("Impossible de créer la playlist");
    }
    });
}
