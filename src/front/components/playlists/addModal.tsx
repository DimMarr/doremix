import { Button } from "@components/generics/button";
import PlaylistRepository from "@repositories/playlistRepository";

// Le bouton que nous allons exporter pour main.tsx
export function AddPlaylistButton() {
  return Button({
    id: "btn-open-add-playlist",
    variant: "primary",
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
      <div class="bg-neutral-900 border border-border p-8 rounded-xl w-full max-w-md shadow-2xl">
        <h2 class="text-2xl font-bold text-foreground mb-6">Create new playlist</h2>

        <form id="add-playlist-form" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-muted-foreground mb-1">Playlist name</label>
            <input type="text" name="name" id="playlist-name-input" required class="w-full px-4 py-2 rounded-lg bg-input border border-border text-foreground focus:ring-2 focus:ring-ring outline-none" />
          </div>

          <div>
            <label class="block text-sm font-medium text-muted-foreground mb-1">Cover image (optional)</label>
            <input type="file" id="playlist-cover-input" accept="image/*" class="w-full px-4 py-2 rounded-lg bg-input border border-border text-foreground file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-primary file:text-primary-foreground hover:file:bg-primary/80" />
          </div>

          <div class="flex justify-end gap-3 mt-8">
            {Button({
              id: 'close-modal',
              variant: 'ghost',
              children: 'Cancel',
              type: 'button'
            })}
            {Button({
              variant: 'primary',
              children: 'Create playlist',
              type: 'submit'
            })}
          </div>
        </form>
      </div>
    </div>
  );
}

// Fonction utilitaire pour gérer les événements de la modale
export function setupModalAddPlaylist() {
  const modal = document.getElementById("add-playlist-modal");
  const openBtn = document.getElementById("btn-open-add-playlist");
  const closeBtn = document.getElementById("close-modal");
  const form = document.getElementById("add-playlist-form") as HTMLFormElement;
  const imageInput = document.getElementById("playlist-cover-input") as HTMLInputElement;

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
      alert("Playlist name cannot be empty");
      return;
    }

    try {
      const playlistresponse = await PlaylistRepository.create(name);

      try {
        if (imageInput.files?.length) {
          await PlaylistRepository.uploadCover(playlistresponse.idPlaylist, imageInput.files[0]);
        }
      } catch (err) {
        console.error(err);
        alert("Playlist created without image due to an error")
      }
      form.reset();
      toggleModal();
      window.location.reload();
    } catch (err) {
      console.error(err);
      alert("Impossible to create playlist");
    }

  });
}

export function setupPlaylistAndTrackModals(){
  const addPlaylistSection = document.getElementById("addPlaylistSection");

  const modalContainer = document.getElementById("modal-container");
  if (addPlaylistSection) {
    addPlaylistSection.innerHTML = AddPlaylistButton();
  }
  if (modalContainer) {
    modalContainer.innerHTML = AddPlaylistModal();
  }
  setupModalAddPlaylist();
}
