import { Genre } from "@models/genre";
import { GenreRepository, ModerationRepository } from "@repositories/index";
import type { ModerationUser } from "@repositories/moderationRepository";
import { AlertManager } from "@utils/alertManager";
import { authService } from "@utils/authentication";

function renderGenreRows(genres: Genre[], editingId: number | null): string {
  if (genres.length === 0) {
    return '<p class="text-muted-foreground text-sm">No genres yet.</p>';
  }

  return genres
    .map((genre) => {
      if (editingId === genre.idGenre) {
        return (
          <div class="flex items-center gap-2 p-2 rounded-lg bg-white/5" data-genre-id={genre.idGenre}>
            <input
              type="text"
              class="flex-1 px-3 py-1 rounded-lg bg-input border border-border text-foreground text-sm focus:ring-2 focus:ring-ring outline-none"
              id={`edit-input-${genre.idGenre}`}
              value={genre.label}
            />
            <button data-save-genre={genre.idGenre} class="px-3 py-1 rounded-lg bg-green-600 text-white text-xs font-medium hover:bg-green-500 transition-colors">Save</button>
            <button data-cancel-edit class="px-3 py-1 rounded-lg bg-neutral-700 text-white text-xs font-medium hover:bg-neutral-600 transition-colors">Cancel</button>
          </div>
        );
      }

      return (
        <div class="flex items-center justify-between p-2 rounded-lg hover:bg-white/5 transition-colors" data-genre-id={genre.idGenre}>
          <span safe class="text-foreground text-sm">{genre.label}</span>
          <div class="flex gap-2">
            <button data-edit-genre={genre.idGenre} class="px-3 py-1 rounded-lg bg-neutral-700 text-white text-xs font-medium hover:bg-neutral-600 transition-colors">Edit</button>
            <button data-delete-genre={genre.idGenre} class="px-3 py-1 rounded-lg bg-red-600/80 text-white text-xs font-medium hover:bg-red-500 transition-colors">Delete</button>
          </div>
        </div>
      );
    })
    .join("");
}

export async function AdminPage(container: HTMLElement | null) {
  if (!container) return;

  const userInfos = await authService.infos();
  const isAdmin = userInfos.role === "ADMIN";
  const isModerator = userInfos.role === "MODERATOR";

  if (!isAdmin && !isModerator) {
    container.innerHTML = (
      <div class="py-12 text-center">
        <h1 class="text-2xl font-bold mb-2">Forbidden</h1>
        <p class="text-muted-foreground mb-6">Only admins and moderators can access this page.</p>
        <a href="/" data-link class="px-4 py-2 rounded-lg bg-neutral-700 text-white text-sm font-medium hover:bg-neutral-600 transition-colors">Back to Home</a>
      </div>
    );
    return;
  }

  if (isAdmin) {
    container.innerHTML = (
      <div class="px-4 py-6 md:px-8">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h1 class="text-3xl font-bold tracking-tight text-white/90">Admin</h1>
            <p class="text-white/60 mt-1 text-sm">Manage genres</p>
          </div>
          <a href="/" data-link class="px-4 py-2 rounded-lg bg-neutral-700 text-white text-sm font-medium hover:bg-neutral-600 transition-colors">
            Back
          </a>
        </div>

        <div class="bg-neutral-900 border border-border p-6 rounded-xl w-full max-w-2xl shadow-2xl">
          <h2 class="text-xl font-semibold text-white mb-4">Genres</h2>
          <div id="genre-list" class="space-y-2 mb-6 max-h-96 overflow-y-auto">
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
    await initGenreManagement(container);
    return;
  }

  container.innerHTML = (
    <div class="px-4 py-6 md:px-8">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-3xl font-bold tracking-tight text-white/90">Moderation</h1>
          <p class="text-white/60 mt-1 text-sm">Ban non-admin users and revoke their tokens</p>
        </div>
        <a href="/" data-link class="px-4 py-2 rounded-lg bg-neutral-700 text-white text-sm font-medium hover:bg-neutral-600 transition-colors">
          Back
        </a>
      </div>

      <div class="bg-neutral-900 border border-border p-6 rounded-xl w-full shadow-2xl min-h-[70vh]">
        <h2 class="text-xl font-semibold text-white mb-4">Ban candidates</h2>
        <div id="ban-user-list" class="space-y-3 overflow-y-auto h-[calc(70vh-5rem)]">
          <p class="text-muted-foreground text-sm">Loading...</p>
        </div>
      </div>
    </div>
  );

  await initModerationPanel(container);
}

function renderBanRows(users: ModerationUser[]): string {
  if (users.length === 0) {
    return '<p class="text-muted-foreground text-sm">No ban candidates available.</p>';
  }

  return users
    .map((user) => (
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 p-3 rounded-lg border border-white/10 bg-white/5" data-user-id={user.idUser}>
        <div>
          <p safe class="text-white text-sm font-medium">{user.username}</p>
          <p safe class="text-white/60 text-xs">{user.email}</p>
          <span class="inline-block mt-2 px-2 py-1 rounded-full bg-neutral-700 text-white text-[10px] uppercase tracking-wide">
            {user.role}
          </span>
        </div>
        <button data-ban-user={user.idUser} class="px-3 py-2 rounded-lg bg-red-600 text-white text-xs font-medium hover:bg-red-500 transition-colors self-start md:self-auto">
          Ban user
        </button>
      </div>
    ))
    .join("");
}

async function initGenreManagement(container: HTMLElement) {
  const genreList = container.querySelector("#genre-list") as HTMLElement | null;
  const addForm = container.querySelector("#add-genre-form") as HTMLFormElement | null;
  const newGenreInput = container.querySelector("#new-genre-input") as HTMLInputElement | null;

  if (!genreList || !addForm || !newGenreInput) return;

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

  genreList.addEventListener("click", async (event) => {
    const target = event.target as HTMLElement;

    const editBtn = target.closest("[data-edit-genre]") as HTMLElement | null;
    if (editBtn) {
      editingId = parseInt(editBtn.getAttribute("data-edit-genre") || "", 10);
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
      const id = parseInt(saveBtn.getAttribute("data-save-genre") || "", 10);
      const input = container.querySelector(`#edit-input-${id}`) as HTMLInputElement | null;
      const newLabel = input?.value.trim();
      if (!newLabel) return;

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
      const id = parseInt(deleteBtn.getAttribute("data-delete-genre") || "", 10);
      if (!confirm("Delete this genre? This will fail if any playlist uses it.")) return;

      try {
        await repo.delete(id);
        new AlertManager().success("Genre deleted");
        await refresh();
      } catch {
        new AlertManager().error("Cannot delete genre - it may still be in use");
      }
    }
  });

  addForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const label = newGenreInput.value.trim();
    if (!label) return;

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

  await refresh();
}

async function initModerationPanel(container: HTMLElement) {
  const userList = container.querySelector("#ban-user-list") as HTMLElement | null;
  if (!userList) return;

  const repo = new ModerationRepository();
  let users: ModerationUser[] = [];

  const refresh = async () => {
    try {
      users = await repo.getBanCandidates();
      userList.innerHTML = renderBanRows(users);
    } catch {
      userList.innerHTML = '<p class="text-red-400 text-sm">Failed to load users.</p>';
    }
  };

  userList.addEventListener("click", async (event) => {
    const target = event.target as HTMLElement;
    const banBtn = target.closest("[data-ban-user]") as HTMLElement | null;
    if (!banBtn) return;

    const userId = parseInt(banBtn.getAttribute("data-ban-user") || "", 10);
    if (!userId) return;

    if (!confirm("Ban this user and revoke all of their tokens?")) return;

    try {
      banBtn.setAttribute("disabled", "true");
      banBtn.classList.add("opacity-70", "cursor-not-allowed");
      await repo.banUser(userId);
      new AlertManager().success("User banned and logged out");
      users = users.filter((user) => user.idUser !== userId);
      userList.innerHTML = renderBanRows(users);
    } catch {
      new AlertManager().error("Failed to ban user");
      banBtn.removeAttribute("disabled");
      banBtn.classList.remove("opacity-70", "cursor-not-allowed");
    }
  });

  await refresh();
}
