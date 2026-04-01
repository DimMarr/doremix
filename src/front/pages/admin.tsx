import { Genre, User } from "@models/index";
import { GenreRepository, ModerationRepository, UserRepository } from "@repositories/index";
import { Input, AdminPanel } from "@components/index";
import type { ModerationUser } from "@repositories/moderationRepository";
import { AlertManager } from "@utils/alertManager";
import { authService } from "@utils/authentication";
import { PlaylistRepository } from "@repositories/playlistRepository";
import Playlist, { Visibility } from "@models/playlist";
import { Track } from "@models/track";

// Main function : Handle behavior based on role
export async function AdminPage(container: HTMLElement | null) {
  if (!container) return;

  const userInfos = await authService.infos();
  const isAdmin = userInfos.role === "ADMIN";
  const isModerator = userInfos.role === "MODERATOR";

  // ROLE == USER
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

  // ROLE == ADMIN
  if (isAdmin) {
    container.innerHTML = (
      <div class="px-4 py-6 md:px-8">
        {/* Header */}
        <div class="flex items-center justify-between mb-6">
          <div>
            <h1 class="text-3xl font-bold tracking-tight text-white/90">Admin Panels</h1>
            <p class="text-white/60 mt-1 text-sm">Manage DoReMiX</p>
          </div>
          <a href="/" data-link class="px-4 py-2 rounded-lg bg-neutral-700 text-white text-sm font-medium hover:bg-neutral-600 transition-colors">
            Back
          </a>
        </div>

        <div class="flex gap-5 items-stretch flex-wrap md:flex-nowrap">
          {/* Genre Managing Panel */}
          <AdminPanel title="Genres" name="genre" content={
            <form id="add-genre-form" class="flex gap-2 mt-4">
              <input
                type="text"
                name="label"
                id="new-genre-input"
                placeholder="New genre name"
                required
                class="flex-1 px-4 py-2 rounded-lg bg-input border border-border text-foreground focus:ring-2 focus:ring-ring outline-none text-sm m-px"
              />
              <button type="submit" class="px-4 py-2 rounded-lg bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/80 transition-colors">
                Add
              </button>
            </form>
          }/>

          {/* Moderators Managing Panel */}
          <AdminPanel title="Moderators" name="moderators"/>
        </div>
      </div>
    );
    await initGenreManagement(container);
    await initAddModeratorPanel(container);
    return;
  }

  // ROLE == MODERATOR
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

      <AdminPanel title="Manage Users" name="ban-user" />
    </div>
  );

  await initModerationPanel(container);
}

/*
 * RENDER FUNCTIONS :
 * renderBanRows()
 * renderGenreRows()
 * renderModeratorRows()
 */

function renderBanRows(users: ModerationUser[]): string {
  if (users.length === 0) {
    return '<p class="text-muted-foreground text-sm">No users available.</p>';
  }

  return users
    .map((user) => {
      const actionButton = user.banned ? (
        <button data-unban-user={user.idUser} class="px-3 py-2 rounded-lg bg-green-600 text-white text-xs font-medium hover:bg-green-500 transition-colors self-start md:self-auto">
          Unban user
        </button>
      ) : (
        <button data-ban-user={user.idUser} class="px-3 py-2 rounded-lg bg-red-600 text-white text-xs font-medium hover:bg-red-500 transition-colors self-start md:self-auto">
          Ban user
        </button>
      );

      return (
        <div class={`flex flex-col md:flex-row md:items-center md:justify-between gap-3 p-3 rounded-lg border border-white/10 ${user.banned ? 'bg-red-900/10 opacity-75' : 'bg-white/5'}`} data-user-id={user.idUser}>
          <div>
            <p class="text-white text-sm font-medium flex items-center gap-1">
              <span safe>{user.username}</span>
              {user.banned ? <span class="text-red-400 text-xs">(Banned)</span> : ""}
            </p>
            <p safe class="text-white/60 text-xs">{user.email}</p>
            <span class="inline-block mt-2 px-2 py-1 rounded-full bg-neutral-700 text-white text-[10px] uppercase tracking-wide">
              {user.role}
            </span>
          </div>
          {actionButton as 'safe'}
        </div>
      );
    })
    .join("");
}

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

function renderModeratorsRows(users: User[]): string {
  if (users.length === 0) {
    return '<p class="text-muted-foreground text-sm">No user.</p>';
  }

  return users
    .map((user) => {
      return (
        <div class="flex items-center justify-between p-2 rounded-lg hover:bg-white/5 transition-colors" data-genre-id={user.idUser}>
          <span safe class="text-foreground text-sm">{user.username}</span>
          <div class="flex gap-2">
            <Input
              type="checkbox"
              checked={user.role === "MODERATOR" || user.role === "ADMIN"}
              disabled={user.role === "ADMIN"}
              data-mod-user={user.idUser}
            />
          </div>
        </div>
      );
    })
    .join("");
}

/*
 * INIT PANEL FUNCTIONS :
 * initGenreManagement()
 * initModeratorPanel()
 * initAddModeratorPanel()
 */


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

async function initAdminPlaylistManagement(container: HTMLElement) {
  const listEl = container.querySelector("#admin-playlist-list") as HTMLElement | null;
  if (!listEl) return;

  const repo = new PlaylistRepository();
  const alerts = new AlertManager();

  let playlists: Playlist[] = [];
  let expandedId: number | null = null;
  let editingId: number | null = null;
  const trackCache: Record<number, Track[]> = {};

  const refresh = async () => {
    try {
      playlists = await repo.adminGetAll();
      listEl.innerHTML = renderPlaylistRows(playlists, expandedId, editingId, trackCache, []);
    } catch {
      listEl.innerHTML = '<p class="text-red-400 text-sm">Failed to load playlists.</p>';
    }
  };

  const loadTracksForPlaylist = async (playlistId: number) => {
    try {
      const tracks = await repo.adminGetTracks(playlistId);
      trackCache[playlistId] = tracks;
      listEl.innerHTML = renderPlaylistRows(playlists, expandedId, editingId, trackCache, []);
    } catch {
      alerts.error("Failed to load tracks");
    }
  };

  listEl.addEventListener("click", async (event) => {
    const target = event.target as HTMLElement;

    const expandBtn = target.closest("[data-expand-playlist]") as HTMLElement | null;
    if (expandBtn) {
      const id = parseInt(expandBtn.getAttribute("data-expand-playlist") || "", 10);
      if (expandedId === id) {
        expandedId = null;
        listEl.innerHTML = renderPlaylistRows(playlists, expandedId, editingId, trackCache, []);
      } else {
        expandedId = id;
        listEl.innerHTML = renderPlaylistRows(playlists, expandedId, editingId, trackCache, []);
        if (!trackCache[id]) {
          await loadTracksForPlaylist(id);
        }
      }
      return;
    }

    const editBtn = target.closest("[data-edit-playlist]") as HTMLElement | null;
    if (editBtn) {
      editingId = parseInt(editBtn.getAttribute("data-edit-playlist") || "", 10);
      listEl.innerHTML = renderPlaylistRows(playlists, expandedId, editingId, trackCache, []);
      return;
    }

    const cancelBtn = target.closest("[data-cancel-playlist-edit]");
    if (cancelBtn) {
      editingId = null;
      listEl.innerHTML = renderPlaylistRows(playlists, expandedId, editingId, trackCache, []);
      return;
    }

    const saveBtn = target.closest("[data-save-playlist]") as HTMLElement | null;
    if (saveBtn) {
      const id = parseInt(saveBtn.getAttribute("data-save-playlist") || "", 10);
      const nameInput = container.querySelector(`#edit-playlist-name-${id}`) as HTMLInputElement | null;
      const visibilitySelect = container.querySelector(`#edit-playlist-visibility-${id}`) as HTMLSelectElement | null;

      const updateData: Record<string, unknown> = {};
      if (nameInput?.value.trim()) updateData.name = nameInput.value.trim();
      if (visibilitySelect?.value) updateData.visibility = visibilitySelect.value;

      try {
        await repo.adminUpdate(id, updateData as Partial<Playlist>);
        alerts.success("Playlist updated");
        editingId = null;
        await refresh();
      } catch {
        alerts.error("Failed to update playlist");
      }
      return;
    }

    const deleteBtn = target.closest("[data-delete-playlist]") as HTMLElement | null;
    if (deleteBtn) {
      const id = parseInt(deleteBtn.getAttribute("data-delete-playlist") || "", 10);
      const playlist = playlists.find((p) => p.idPlaylist === id);
      if (!confirm(`Delete playlist "${playlist?.name}"? This cannot be undone.`)) return;
      try {
        await repo.adminDelete(id);
        alerts.success("Playlist deleted");
        if (expandedId === id) expandedId = null;
        delete trackCache[id];
        await refresh();
      } catch {
        alerts.error("Failed to delete playlist");
      }
      return;
    }

    const removeBtn = target.closest("[data-remove-track]") as HTMLElement | null;
    if (removeBtn) {
      const trackId = parseInt(removeBtn.getAttribute("data-remove-track") || "", 10);
      const playlistId = parseInt(removeBtn.getAttribute("data-remove-track-playlist") || "", 10);
      try {
        await repo.adminRemoveTrack(playlistId, trackId);
        alerts.success("Track removed");
        delete trackCache[playlistId];
        await loadTracksForPlaylist(playlistId);
      } catch {
        alerts.error("Failed to remove track");
      }
      return;
    }
  });

  listEl.addEventListener("submit", async (event) => {
    const form = (event.target as HTMLElement).closest("[data-add-track-form]") as HTMLElement | null;
    if (!form) return;
    event.preventDefault();

    const playlistId = parseInt(form.getAttribute("data-add-track-form") || "", 10);
    const titleInput = form.querySelector("[name='title']") as HTMLInputElement;
    const urlInput = form.querySelector("[name='url']") as HTMLInputElement;
    const title = titleInput.value.trim();
    const url = urlInput.value.trim();
    if (!title || !url) return;

    try {
      await repo.adminAddTrack(playlistId, url, title);
      alerts.success("Track added");
      titleInput.value = "";
      urlInput.value = "";
      delete trackCache[playlistId];
      await loadTracksForPlaylist(playlistId);
    } catch {
      alerts.error("Failed to add track");
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
      // On récupère les utilisateurs à bannir et ceux déjà bannis
      const banCandidates = await repo.getBanCandidates();
      const unbanCandidates = await repo.getUnbanCandidates();

      // On fusionne les deux listes et on trie par ID
      users = [...banCandidates, ...unbanCandidates];
      users.sort((a, b) => a.idUser - b.idUser);

      userList.innerHTML = renderBanRows(users);
    } catch {
      userList.innerHTML = '<p class="text-red-400 text-sm">Failed to load users.</p>';
    }
  };

  userList.addEventListener("click", async (event) => {
    const target = event.target as HTMLElement;

    // Gestion du bouton Ban
    const banBtn = target.closest("[data-ban-user]") as HTMLElement | null;
    if (banBtn) {
      const userId = parseInt(banBtn.getAttribute("data-ban-user") || "", 10);
      if (!userId) return;

      if (!confirm("Ban this user and revoke all of their tokens?")) return;

      try {
        banBtn.setAttribute("disabled", "true");
        banBtn.classList.add("opacity-70", "cursor-not-allowed");
        await repo.banUser(userId);
        new AlertManager().success("User banned and logged out");
        await refresh(); // Recharger les données depuis le serveur
      } catch {
        new AlertManager().error("Failed to ban user");
        banBtn.removeAttribute("disabled");
        banBtn.classList.remove("opacity-70", "cursor-not-allowed");
      }
      return;
    }

    // Gestion du bouton Unban
    const unbanBtn = target.closest("[data-unban-user]") as HTMLElement | null;
    if (unbanBtn) {
      const userId = parseInt(unbanBtn.getAttribute("data-unban-user") || "", 10);
      if (!userId) return;

      if (!confirm("Unban this user?")) return;

      try {
        unbanBtn.setAttribute("disabled", "true");
        unbanBtn.classList.add("opacity-70", "cursor-not-allowed");
        await repo.unbanUser(userId);
        new AlertManager().success("User unbanned");
        await refresh(); // Recharger les données depuis le serveur
      } catch {
        new AlertManager().error("Failed to unban user");
        unbanBtn.removeAttribute("disabled");
        unbanBtn.classList.remove("opacity-70", "cursor-not-allowed");
      }
      return;
    }
  });

  await refresh();
}

async function initAddModeratorPanel(container: HTMLElement) {
  // Get panel element
  const moderatorListPanel = container.querySelector("#moderators-list") as HTMLElement | null;
  if (!moderatorListPanel) return;

  // Get users
  const userRepo = new UserRepository();
  let users: User[] = [];

  // Fill panel with users
  const refresh = async () => {
    try {
      users = await userRepo.getAllUsers();
      moderatorListPanel.innerHTML = renderModeratorsRows(users);
    } catch {
      moderatorListPanel.innerHTML = '<p class="text-red-400 text-sm">Failed to load users.</p>';
    }
  };

  // Handle checkbox
  moderatorListPanel.addEventListener("click", async (event) => {
    const target = event.target as HTMLElement;
    const checkbox = target.closest("[data-mod-user]") as HTMLElement | null;
    const role = checkbox.checked ? "USER" : "MODERATOR"

    if (!checkbox) return;

    const userId = parseInt(checkbox.getAttribute("data-mod-user") || "", 10);
    if (!userId) return;

    // If role == "USER" -> addModerator(userId)
    // If role == "MODERATOR" -> demoteModerator(userId)

    try {
      checkbox.setAttribute("disabled", "true");
      checkbox.classList.add("opacity-70", "cursor-not-allowed");

      if (role == "USER") {
        if (!confirm("Do you really want to promote user as moderator?")) return;
        await userRepo.addModerator(userId)
        new AlertManager().success("User is now a moderator.");
        users = users.map((user) => user.idUser === userId ? {...user, role: "MODERATOR"} : user);
      }

      if (role == "MODERATOR") {
        if (!confirm("Do you really want to demote this moderator?")) return;
        await userRepo.demoteModerator(userId)
        new AlertManager().success("User is no longer a moderator.");
        users = users.map((user) => user.idUser === userId ? {...user, role: "USER"} : user);
      }

      moderatorListPanel.innerHTML = renderModeratorsRows(users);

    } catch {
      new AlertManager().error("Failed to changed user's role.");
      checkbox.removeAttribute("disabled");
      checkbox.classList.remove("opacity-70", "cursor-not-allowed");
    }
  });

  await refresh();
}
