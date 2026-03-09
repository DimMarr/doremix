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
      <div id="visibility-trigger" class={`${badgeBase} ${colorClass} ${ canEditVisibility ? interactable : locked}`} data-visibility-trigger>
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
            { visibility !== Visibility.private && (
              <button class={menuOptionClass} data-visibility-option={Visibility.private}>
                {getIconForVisibility(Visibility.private) as 'safe'}
                <span>Private</span>
              </button>
            )}
            { visibility !== Visibility.public && (
              <button class={menuOptionClass} data-visibility-option={Visibility.public}>
                {getIconForVisibility(Visibility.public) as 'safe'}
                <span>Public</span>
              </button>
            )}
            { visibility !== Visibility.open && await isAdmin() &&
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

async function getSharedUsersElement(repo: PlaylistRepository, playlist: Playlist, isPlaylistOwner: boolean): Promise<string> {
  const adminUser = await isAdmin();
  if (!isPlaylistOwner && !adminUser) return '';

  let users: any[] = [];
  try {
    users = await repo.sharedWith(playlist.idPlaylist);
  } catch {
    return '';
  }

  if (users.length === 0) return '';

  const MAX_VISIBLE = 5;
  const visible = users.slice(0, MAX_VISIBLE);
  const overflow = users.length - MAX_VISIBLE;

  const avatars = visible.map((u: any) => {
    const name: string = u.user?.username ?? `#${u.idUser}`;
    const initial = u.username.charAt(0).toUpperCase();
    const roleTitle = u.editor ? `${u.username} (Editor)` : `${u.username} (Viewer)`;
    return `<div
      title="${roleTitle}"
      class="shared-user-avatar flex items-center justify-center w-7 h-7 rounded-full bg-neutral-700 border-2 border-neutral-900 text-xs font-semibold text-white -ml-2 first:ml-0 cursor-default select-none hover:z-10 hover:scale-110 transition-transform"
    >${initial}</div>`;
  }).join('');

  const overflowBadge = overflow > 0
      ? `<div class="flex items-center justify-center w-7 h-7 rounded-full bg-neutral-600 border-2 border-neutral-900 text-xs font-semibold text-muted-foreground -ml-2 select-none">+${overflow}</div>`
      : '';

  return `
    <div id="shared-users-section" class="flex items-center gap-2 mt-1">
      <div class="flex items-center">
        ${avatars}
        ${overflowBadge}
      </div>
      <span class="text-xs text-muted-foreground">${users.length} ${users.length === 1 ? 'person' : 'people'} with access</span>
    </div>
  `;
}

function renderTrackList(playlist: Playlist): string {
  const tracks = playlist.tracks || [];
  const currentTrack = trackPlayerInstance.getCurrentTrack();
  const playerState = trackPlayerInstance.getPlayerState();

  return (
    <div>
      <TrackListHeader />
      {tracks.map(async (track, index) => ( await
        <TrackRow
          track={track}
          index={index}
          playlistId={playlist.idPlaylist}
          trackPlayer={trackPlayerInstance}
          current_track={[YoutubePlayerState.UNSTARTED, YoutubePlayerState.CUED].includes(playerState) ? null : currentTrack}
        />
      )) as 'safe'}
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
          {await getSharedUsersElement(repo, playlist, isPlaylistOwner) as 'safe'}
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

  const handleShare = async () => {
    const modalContainer = container.querySelector('#modal-container');
    if (!modalContainer) return;

    const isPlaylistOwner = await isOwner(playlist);
    const adminUser = await isAdmin();

    const { render } = ShareModal({
      playlistId: playlist.idPlaylist,
      isOwnerOrAdmin: isPlaylistOwner || adminUser,
      onClose: () => {
        modalContainer.innerHTML = '';
        updateHeader();
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
          { await canEdit(repo, playlist) && <Button id="add-track-button" variant="outline" size="md">Add Track</Button> }
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
          {await getSharedUsersElement(repo, playlist, isPlaylistOwner) as 'safe'}
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
}
