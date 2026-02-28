import { GenreRepository } from "@repositories/index";
import { Genre } from "@models/genre";
import { AlertManager } from "@utils/alertManager";

export function GenreManageModal() {
  return (
    <div id="genre-manage-modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm hidden">
      <div class="bg-neutral-900 border border-border p-8 rounded-xl w-full max-w-lg shadow-2xl">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-foreground">Manage Genres</h2>
          <button id="close-genre-modal" class="text-muted-foreground hover:text-foreground transition-colors text-xl font-bold">✕</button>
        </div>

        <div id="genre-list" class="space-y-2 mb-6 max-h-72 overflow-y-auto">
          <p class="text-muted-foreground text-sm">Loading...</p>
        </div>

        <form id="add-genre-form" class="flex gap-2 mt-4">
          <input
            type="text"
            name="label"
            id="new-genre-input"
            placeholder="New genre name"
            required
            class="flex-1 px-4 py-2 rounded-lg bg-input border border-border text-foreground focus:ring-2 focus:ring-ring outline-none text-sm"
          />
          <button type="submit" class="px-4 py-2 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/80 transition-colors">
            Add
          </button>
        </form>
      </div>
    </div>
  );
}

function renderGenreRows(genres: Genre[], editingId: number | null): string {
  if (genres.length === 0) {
    return '<p class="text-muted-foreground text-sm">No genres yet.</p>';
  }

  return genres.map(g => {
    if (editingId === g.idGenre) {
      return (
        <div class="flex items-center gap-2 p-2 rounded-lg bg-white/5" data-genre-id={g.idGenre}>
          <input
            type="text"
            class="flex-1 px-3 py-1 rounded-lg bg-input border border-border text-foreground text-sm focus:ring-2 focus:ring-ring outline-none"
            id={`edit-input-${g.idGenre}`}
            value={g.label}
          />
          <button data-save-genre={g.idGenre} class="px-3 py-1 rounded-lg bg-green-600 text-white text-xs font-medium hover:bg-green-500 transition-colors">Save</button>
          <button data-cancel-edit class="px-3 py-1 rounded-lg bg-neutral-700 text-white text-xs font-medium hover:bg-neutral-600 transition-colors">Cancel</button>
        </div>
      );
    }
    return (
      <div class="flex items-center justify-between p-2 rounded-lg hover:bg-white/5 transition-colors" data-genre-id={g.idGenre}>
        <span safe class="text-foreground text-sm">{g.label}</span>
        <div class="flex gap-2">
          <button data-edit-genre={g.idGenre} class="px-3 py-1 rounded-lg bg-neutral-700 text-white text-xs font-medium hover:bg-neutral-600 transition-colors">Edit</button>
          <button data-delete-genre={g.idGenre} class="px-3 py-1 rounded-lg bg-red-600/80 text-white text-xs font-medium hover:bg-red-500 transition-colors">Delete</button>
        </div>
      </div>
    );
  }).join('');
}

export function setupGenreManageModal() {
  const modal = document.getElementById("genre-manage-modal");
  const openBtn = document.getElementById("btn-open-genre-manage");
  const closeBtn = document.getElementById("close-genre-modal");
  const genreList = document.getElementById("genre-list");
  const addForm = document.getElementById("add-genre-form") as HTMLFormElement;
  const newGenreInput = document.getElementById("new-genre-input") as HTMLInputElement;

  if (!modal || !openBtn || !closeBtn || !genreList || !addForm) return;

  const repo = new GenreRepository();
  let genres: Genre[] = [];
  let editingId: number | null = null;

  const refresh = async () => {
    try {
      genres = await repo.getAll();
      genreList.innerHTML = renderGenreRows(genres, editingId);
    } catch {
      genreList.innerHTML = '<p class="text-red-400 text-sm">Failed to load genres.</p>';
    }
  };

  const toggleModal = () => modal.classList.toggle("hidden");

  openBtn.addEventListener("click", () => {
    editingId = null;
    refresh();
    toggleModal();
  });

  closeBtn.addEventListener("click", toggleModal);

  modal.addEventListener("click", (e) => {
    if (e.target === modal) toggleModal();
  });

  genreList.addEventListener("click", async (e) => {
    const target = e.target as HTMLElement;

    const editBtn = target.closest("[data-edit-genre]") as HTMLElement | null;
    if (editBtn) {
      editingId = parseInt(editBtn.getAttribute("data-edit-genre")!, 10);
      genreList.innerHTML = renderGenreRows(genres, editingId);
      return;
    }

    const cancelBtn = target.closest("[data-cancel-edit]");
    if (cancelBtn) {
      editingId = null;
      genreList.innerHTML = renderGenreRows(genres, editingId);
      return;
    }

    const saveBtn = target.closest("[data-save-genre]") as HTMLElement | null;
    if (saveBtn) {
      const id = parseInt(saveBtn.getAttribute("data-save-genre")!, 10);
      const input = document.getElementById(`edit-input-${id}`) as HTMLInputElement | null;
      const newLabel = input?.value.trim();
      if (!newLabel) return;

      // NOUVEAU: Vérification client anti-doublon
      if (genres.some((g) => g.label.toLowerCase() === newLabel.toLowerCase() && g.idGenre !== id)) {
        new AlertManager().error("This genre already exists");
        return;
      }

      try {
        await repo.update(id, newLabel);
        new AlertManager().success("Genre updated");
        editingId = null;
        await refresh();
      } catch (error: any) {
        if (error.message === "Conflict") {
          new AlertManager().error("This genre already exists");
        } else {
          new AlertManager().error("Failed to update genre");
        }
      }
      return;
    }

    const deleteBtn = target.closest("[data-delete-genre]") as HTMLElement | null;
    if (deleteBtn) {
      const id = parseInt(deleteBtn.getAttribute("data-delete-genre")!, 10);
      if (!confirm("Delete this genre? This will fail if any playlist uses it.")) return;
      try {
        await repo.delete(id);
        new AlertManager().success("Genre deleted");
        await refresh();
      } catch {
        new AlertManager().error("Cannot delete genre — it may still be in use");
      }
    }
  });

  addForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const label = newGenreInput.value.trim();
    if (!label) return;

    // NOUVEAU: Vérification client anti-doublon
    if (genres.some((g) => g.label.toLowerCase() === label.toLowerCase())) {
      new AlertManager().error("This genre already exists");
      return;
    }

    try {
      await repo.create(label);
      new AlertManager().success("Genre created");
      newGenreInput.value = "";
      await refresh();
    } catch (error: any) {
      if (error.message === "Conflict") {
        new AlertManager().error("This genre already exists");
      } else {
        new AlertManager().error("Failed to create genre");
      }
    }
  });
}
