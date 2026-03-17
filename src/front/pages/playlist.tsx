import { TrackRepository } from "@repositories/trackRepository";
import { Button, AddTrackModal, ShareModal } from "@components/index";
import { TrackListHeader } from "@components/tracks/header";
import { TrackRow } from "@components/tracks/row";
import { AlertManager } from "@utils/alertManager";
import { trackPlayerInstance } from "@layouts/mainLayout";
import { YoutubePlayerState } from "@store/trackPlayer";
import { PlaylistRepository } from "@repositories/index";
import Playlist, { Visibility } from "@models/playlist";
import type { Track } from "@models/track";
import { authService } from "@utils/authentication";
import { canDeletePlaylist, canEdit, isAdmin, isOwner } from "@utils/rights";

interface PageParams {
  id: string;
}

// True if playlist is shared, else false
async function isShared(repo: PlaylistRepository, playlist: Playlist) {
  const userInfos = await authService.infos();
  const currentUserId = userInfos.id

  const users = await repo.sharedWith(playlist.idPlaylist)
  const shared_users = users.map(user => user.idUser)
  return shared_users.includes(currentUserId)
}

function getIconForVisibility(visibility: Visibility) {
  switch (visibility.toLowerCase()) {
    case Visibility.private:
      return (
        <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0110 0v4" />
        </svg>
      );
    case Visibility.public:
      return (
        <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M2 12h20" />
          <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z" />
        </svg>
      );
    default:
      return (
        <svg class="w-3.5 h-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 00-3-3.87" />
          <path d="M16 3.13a4 4 0 010 7.75" />
        </svg>
      );
  }
}

async function getVisibilityElement(repo: PlaylistRepository, playlist: Playlist) {
  const visibility = playlist.visibility;
  const badgeBase = "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border uppercase tracking-wider transition-all duration-200 shadow-sm whitespace-nowrap";
  const interactable = "cursor-pointer hover:shadow-md relative select-none";
  const locked = "cursor-not-allowed opacity-80";

  let colorClass = "";
  switch (visibility.toLowerCase()) {
    case Visibility.private:
      colorClass = "bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20";
      break;
    case Visibility.public:
      colorClass = "bg-green-500/10 text-green-500 border-green-500/20 hover:bg-green-500/20";
      break;
    case Visibility.open:
      colorClass = "bg-purple-500/10 text-purple-500 border-purple-500/20 hover:bg-purple-500/20";
      break;
    default:
      colorClass = "bg-blue-500/10 text-blue-500 border-blue-500/20 hover:bg-blue-500/20";
      break;
  }

  let canEditVisibility = false;
  if (await canEdit(repo, playlist) && (playlist.visibility != Visibility.open || isAdmin())) {
    canEditVisibility = true;
  }

  const menuOptionClass = "w-full text-left px-4 py-3 text-sm font-medium text-white hover:bg-white/10 flex items-center gap-2 transition-colors active:bg-white/20";

  return (
    <div class="relative z-20 w-fit">
      <div id="visibility-trigger" class={`${badgeBase} ${colorClass} ${canEditVisibility ? interactable : locked}`} data-visibility-trigger>
        <div class="flex items-center gap-2 pointer-events-none">
          {getIconForVisibility(visibility) as 'safe'}
          <span>{visibility} {await isShared(repo, playlist) ? "(SHARED)" : ""}</span>
          {canEditVisibility && <svg class="w-3 h-3 opacity-60 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>}
        </div>
      </div>
      {canEditVisibility &&
        <div id="visibility-menu" class="hidden absolute top-full left-0 mt-2 w-48 bg-neutral-900 border border-white/10 rounded-xl shadow-xl overflow-hidden backdrop-blur-md origin-top-left transition-all z-50 animate-in fade-in zoom-in-95 duration-200">
          <div class="flex flex-col py-1">
            {visibility !== Visibility.private && (
              <button class={menuOptionClass} data-visibility-option={Visibility.private}>
                {getIconForVisibility(Visibility.private) as 'safe'}
                <span>Private</span>
              </button>
            )}
            {visibility !== Visibility.public && (
              <button class={menuOptionClass} data-visibility-option={Visibility.public}>
                {getIconForVisibility(Visibility.public) as 'safe'}
                <span>Public</span>
              </button>
            )}
            {visibility !== Visibility.open && await isAdmin() &&
              <button class={menuOptionClass} data-visibility-option={Visibility.open}>
                {getIconForVisibility(Visibility.open) as 'safe'}
                <span>OPEN</span>
              </button>
            }
          </div>
        </div>
      }
    </div>
  );
}

async function renderTrackList(playlist: Playlist): Promise<string> {
  const tracks = playlist.tracks || [];
  const currentTrack = trackPlayerInstance.getCurrentTrack();
  const playerState = trackPlayerInstance.getPlayerState();

  return (
    <div>
      <TrackListHeader />
      {(await Promise.all(tracks.map(async (track, index) => (
        <TrackRow
          track={track}
          index={index}
          playlistId={playlist.idPlaylist}
          current_track={(playerState === YoutubePlayerState.UNSTARTED || playerState === YoutubePlayerState.CUED) ? undefined : currentTrack}
        />
      )))) as unknown as 'safe'}
    </div>
  );
}

export async function PlaylistDetailPage(
  container: HTMLElement | null,
  onBack: () => void,
  params: PageParams
) {
  if (!container) return;

  const playlistId = parseInt(params.id, 10);
  const repo = new PlaylistRepository();
  let playlist = await repo.getById(playlistId);

  // Local state
  let tracks: Track[] = playlist.tracks || [];

  const updateHeader = async () => {
    const headerContainer = container.querySelector('#playlist-header-info');
    if (headerContainer) {
      const canDeleteCurrentPlaylist = await canDeletePlaylist(playlist);
      const isPlaylistOwner = await isOwner(playlist);

      headerContainer.innerHTML = (
        <>
          {await getVisibilityElement(repo, playlist) as 'safe'}
          {renderGenreSection() as 'safe'}
          <h1 safe class="font-bold text-4xl mt-2">{playlist.name}</h1>
          <p safe class="text-muted-foreground text-lg">{playlist.description || ''}</p>
          <div class="flex flex-wrap gap-2 mt-1">
            {isPlaylistOwner && <Button id="share-button" variant="outline" size="md">Share Playlist</Button>}
            {canDeleteCurrentPlaylist && <Button id="delete-playlist-button" variant="destructive" size="md">Delete Playlist</Button>}
          </div>
        </>
      );
    }
  }

  const handleVisibilityChange = async (newVis: Visibility) => {
    // Optimistic update
    const oldVis = playlist.visibility;
    playlist.visibility = newVis;
    updateHeader();

    // Determine backend enum value (uppercase)
    const backendVis = newVis === Visibility.public ? "PUBLIC" : newVis === Visibility.private ? "PRIVATE" : "OPEN";

    try {
      await repo.update(playlist.idPlaylist!, { visibility: backendVis as any });
      new AlertManager().success(`Playlist is now ${newVis}`);
    } catch (err) {
      console.error("Failed to update visibility", err);
      new AlertManager().error("Failed to update visibility");
      // Revert
      playlist.visibility = oldVis;
      updateHeader();
    }
  };

  const updateTrackListDisplay = async () => {
    const trackListContainer = container.querySelector('#track-list-container');
    if (trackListContainer) {
      trackListContainer.innerHTML = await renderTrackList({ ...playlist, tracks });
    }
  };

  const handleAddTrack = () => {
    const modalContainer = container.querySelector('#modal-container');
    if (!modalContainer) return;

    const { render } = AddTrackModal({
      playlistId: playlist.idPlaylist,
      onClose: () => {
        modalContainer.innerHTML = '';
      },
      onTrackAdded: (newTrack: Track) => {
        tracks = [...tracks, newTrack];
        trackPlayerInstance.setPlaylist({ ...playlist, tracks });
        updateTrackListDisplay();
        modalContainer.innerHTML = '';
      }
    });
    render(modalContainer);
  };

  const handleShare = () => {
    const modalContainer = container.querySelector('#modal-container');
    if (!modalContainer) return;

    const { render } = ShareModal({
      playlistId: playlist.idPlaylist,
      onClose: () => {
        modalContainer.innerHTML = '';
      }
    });
    render(modalContainer);
  };

  const handleDeletePlaylist = async () => {
    if (!playlist.idPlaylist) return;
    if (!(await canDeletePlaylist(playlist))) return;

    if (!confirm(`Delete "${playlist.name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await repo.delete(playlist.idPlaylist);

      if (trackPlayerInstance.playlist?.idPlaylist === playlist.idPlaylist) {
        trackPlayerInstance.stopVideo();
        trackPlayerInstance.setPlaylist(new Playlist({ tracks: [] }));
      }

      new AlertManager().success("Playlist deleted");
      onBack();
    } catch (err) {
      console.error("Failed to delete playlist", err);
      new AlertManager().error("Failed to delete playlist");
    }
  };

  const handleDeleteTrack = async (trackIndex: number) => {
    const track = tracks[trackIndex];
    if (!track) return;

    const wasPlaying = trackPlayerInstance.getCurrentTrack()?.idTrack === track.idTrack;

    // On supprime la playlist du track store.
    tracks = tracks.filter((_, i) => i !== trackIndex);
    playlist.tracks = tracks;
    trackPlayerInstance.setPlaylist({ ...playlist });

    // Si la track supprimée était en cours on la stoppe et on passe à la track suivante (s'il reste des tracks)
    if (wasPlaying) {
      trackPlayerInstance.stopVideo();
      if (tracks.length > 0) {
        trackPlayerInstance.nextTrack();
      }
    }

    updateTrackListDisplay();

    try {
      await new TrackRepository().delete(playlist.idPlaylist, track.idTrack);
    } catch (err) {
      console.error(err);
      new AlertManager().error("Failed to remove track");

      // S'il y a une erreur lors de la suppression du track, on revient en arrière en affichant la track qui n'a pas pu être supprimé.
      tracks.splice(trackIndex, 0, track);
      playlist.tracks = tracks;
      trackPlayerInstance.setPlaylist({ ...playlist });
      updateTrackListDisplay();
    }
  };

  const handlePlayTrack = (index: number) => {
    if (trackPlayerInstance.playlist?.idPlaylist !== playlist.idPlaylist) {
      trackPlayerInstance.setPlaylist({ ...playlist, tracks });
    }
    trackPlayerInstance.playTrack(index);
  };

  // Render page
  function renderGenreSection() {
    if (!playlist.genreLabel) return '';

    return (
      <span class="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-wider">
        {playlist.genreLabel}
      </span>
    );
  }

  const canDeleteCurrentPlaylist = await canDeletePlaylist(playlist);
  const isPlaylistOwner = await isOwner(playlist);

  container.innerHTML = (
    <div>
      <div id="modal-container"></div>

      <div class="mb-8">
        <Button id="back-button" variant="ghost" size="sm">← Back</Button>
      </div>

      <div class="flex items-start gap-8 my-8">
        <div class="flex flex-col items-center gap-4">
          <img
            src={playlist.image}
            class="w-48 h-48 rounded-md object-cover shadow-2xl"
            alt={playlist.name}
          />
          {await canEdit(repo, playlist) && <Button id="add-track-button" variant="outline" size="md">Add Track</Button>}
        </div>
        <div id="playlist-header-info" class="pt-2 flex flex-col items-start gap-2">
          {await getVisibilityElement(repo, playlist) as 'safe'}
          {renderGenreSection() as 'safe'}
          <h1 safe class="font-bold text-4xl mt-2">{playlist.name}</h1>
          <p safe class="text-muted-foreground text-lg">{playlist.description || ''}</p>
          <div class="flex flex-wrap gap-2 mt-1">
            {isPlaylistOwner && <Button id="share-button" variant="outline" size="md">Share Playlist</Button>}
            {canDeleteCurrentPlaylist && <Button id="delete-playlist-button" variant="destructive" size="md">Delete Playlist</Button>}
          </div>
        </div>
      </div>

      <div id="track-list-container" class="flex flex-col gap-4">
        {await renderTrackList({ ...playlist, tracks }) as 'safe'}
      </div>
    </div>
  );

  // Initialize functionality
  updateTrackListDisplay();

  // Event delegation
  container.onclick = (e: MouseEvent) => {
    const target = e.target as HTMLElement;

    // Visibility Dropdown Logic
    const menu = container.querySelector('#visibility-menu');
    const trigger = target.closest('[data-visibility-trigger]');

    // Toggle Menu
    if (trigger) {
      e.stopPropagation();
      menu?.classList.toggle('hidden');
      // Close other menus if any? (we assume only one here)
      return;
    }

    // Handle Option Selection
    const option = target.closest('[data-visibility-option]') as HTMLElement | null;
    if (option) {
      e.stopPropagation();
      const newVis = option.getAttribute('data-visibility-option') as Visibility;
      if (newVis) {
        handleVisibilityChange(newVis);
      }
      menu?.classList.add('hidden');
      return;
    }

    // Close menu when clicking outside (since we used stopPropagation on trigger/option, any bubbling click here is "outside" for them)
    // But wait, if we click somewhere else inside `container`, this handler fires.
    // If we click inside the menu but not on an option (e.g. padding), we should probably not close?
    // Let's refine:
    if (menu && !menu.classList.contains('hidden') && !menu.contains(target)) {
      menu.classList.add('hidden');
    }

    if (target.closest('#back-button')) {
      onBack();
      return;
    }

    if (target.closest('#add-track-button')) {
      handleAddTrack();
      return;
    }

    if (target.closest('#share-button')) {
      handleShare();
      return;
    }

    if (target.closest('#delete-playlist-button')) {
      handleDeletePlaylist();
      return;
    }

    const deleteButton = target.closest('.delete-track') as HTMLElement | null;
    if (deleteButton) {
      e.stopPropagation();
      const trackIndex = Number(deleteButton.getAttribute('data-track-index'));
      if (!Number.isNaN(trackIndex)) {
        handleDeleteTrack(trackIndex);
      }
      return;
    }

    const row = target.closest('[data-track-index]') as HTMLElement | null;
    if (row) {
      const index = Number(row.getAttribute('data-track-index'));
      if (!Number.isNaN(index)) {
        handlePlayTrack(index);
      }
    }
  };

  // Drag & Drop Event Delegation
  let draggedTrackIndex: number | null = null;
  let draggedTrackId: number | null = null;
  let draggedRow: HTMLElement | null = null;
  let placeholder: HTMLElement | null = null;

  container.addEventListener('dragstart', (e: DragEvent) => {
    const target = e.target as HTMLElement;
    const row = target.closest('[data-track-index]') as HTMLElement;
    if (row && e.dataTransfer) {
      draggedTrackIndex = Number(row.getAttribute('data-track-index'));
      draggedTrackId = Number(row.getAttribute('data-track-id'));
      draggedRow = row;

      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', draggedTrackIndex.toString());

      // Create a custom drag image for better UI
      const dragImage = row.cloneNode(true) as HTMLElement;
      dragImage.style.width = `${row.offsetWidth}px`;
      dragImage.classList.add('bg-neutral-800', 'shadow-2xl', 'scale-105', 'opacity-90', 'rounded-md', 'z-50', 'pointer-events-none');
      document.body.appendChild(dragImage);
      dragImage.style.position = 'absolute';
      dragImage.style.top = '-1000px';
      e.dataTransfer.setDragImage(dragImage, e.offsetX || 20, e.offsetY || 20);

      // Create the placeholder
      placeholder = document.createElement('div');
      placeholder.id = 'dnd-placeholder';
      placeholder.className = "bg-blue-500/10 border-2 border-dashed border-blue-500/50 rounded-md transition-all duration-300 pointer-events-none";
      placeholder.style.height = `${row.offsetHeight}px`;

      // Wait for drag start to finish before hiding visually
      setTimeout(() => {
        row.style.display = 'none'; // Keep it simple to remove from flow
        row.parentNode?.insertBefore(placeholder!, row);
      }, 0);

      // Clean up the temporary drag image from body
      setTimeout(() => {
        if (document.body.contains(dragImage)) {
          document.body.removeChild(dragImage);
        }
      }, 100);
    }
  });

  container.addEventListener('dragover', (e: DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer) e.dataTransfer.dropEffect = 'move';

    if (!placeholder || !draggedRow) return;

    const wrapper = container.querySelector('#track-list-container > div');
    if (!wrapper) return;

    // Find all track rows in the wrapper excluding the dragged one and the placeholder
    const allItems = Array.from(wrapper.children) as HTMLElement[];
    const visibleRows = allItems.filter(el => el !== draggedRow && el !== placeholder && el.hasAttribute('data-track-index'));

    let insertBeforeNode: HTMLElement | null = null;

    // Determine the position based on cursor Y coordinate
    for (let i = 0; i < visibleRows.length; i++) {
      const r = visibleRows[i];
      const rect = r.getBoundingClientRect();
      const midY = rect.top + rect.height / 2;

      if (e.clientY < midY) {
        insertBeforeNode = r;
        break;
      }
    }

    if (insertBeforeNode) {
      if (placeholder.nextElementSibling !== insertBeforeNode) {
        wrapper.insertBefore(placeholder, insertBeforeNode);
      }
    } else {
      wrapper.appendChild(placeholder);
    }
  });

  container.addEventListener('dragend', (e: DragEvent) => {
    if (draggedRow) {
      draggedRow.style.display = ''; // Restore visibility
    }
    if (placeholder && placeholder.parentNode) {
      placeholder.parentNode.removeChild(placeholder);
    }

    draggedTrackIndex = null;
    draggedTrackId = null;
    draggedRow = null;
    placeholder = null;
  });

  container.addEventListener('drop', async (e: DragEvent) => {
    e.preventDefault();

    if (draggedRow && placeholder && draggedTrackIndex !== null && draggedTrackId !== null) {
      const wrapper = container.querySelector('#track-list-container > div');
      if (wrapper) {
        // Find drop position relative to data-track-index elements.
        // We look at placeholder's position skipping draggedRow
        const allItems = Array.from(wrapper.children) as HTMLElement[];
        const filteredItems = allItems.filter(el => (el.hasAttribute('data-track-index') && el !== draggedRow) || el === placeholder);

        let newIndex = filteredItems.indexOf(placeholder);

        // Remove placeholder and restore dragged row
        if (placeholder.parentNode) placeholder.parentNode.removeChild(placeholder);
        draggedRow.style.display = '';

        if (newIndex !== -1 && newIndex !== draggedTrackIndex) {
          const trackToMove = tracks[draggedTrackIndex];
          tracks.splice(draggedTrackIndex, 1);
          tracks.splice(newIndex, 0, trackToMove);

          playlist.tracks = [...tracks];
          trackPlayerInstance.setPlaylist({ ...playlist });
          updateTrackListDisplay();

          const afterTrackId = newIndex > 0 ? tracks[newIndex - 1].idTrack : null;

          try {
            await repo.reorderTrack(playlist.idPlaylist, draggedTrackId, afterTrackId);
          } catch (err) {
            console.error("Failed to reorder tracks", err);
            new AlertManager().error("Failed to save reorder");
          }
        }
      }
    }

    draggedTrackIndex = null;
    draggedTrackId = null;
    draggedRow = null;
    placeholder = null;
  });
}
