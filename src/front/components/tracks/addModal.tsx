import {PlaylistRepository, TrackRepository} from "@repositories/index";
import { Button, Input } from "@components/generics";
import { isValidEmail } from "@utils/authentication";
import { AlertManager } from "@utils/alertManager";

export function AddTrackModal({ playlistId, onClose, onTrackAdded }) {
  const modalHtml = (
    <div id="add-track-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-neutral-900 border border-border rounded-lg p-8 max-w-md w-full">
        <h2 class="text-2xl font-bold text-foreground mb-4">Add New Track</h2>
        <form id="add-track-form">
          <div class="mb-4">
            <label for="youtube-url" class="block text-sm font-medium text-muted-foreground mb-1">
              YouTube URL
            </label>
            <input
              type="text"
              id="youtube-url"
              name="youtube-url"
              class="w-full px-3 py-2 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-ring bg-input text-foreground"
              placeholder="https://www.youtube.com/watch?v=..."
            />
          </div>
          <div id="track-info" class="mb-4" style="display: none;">
            <label for="track-title" class="block text-sm font-medium text-muted-foreground mb-1">
              Track Title
            </label>
            <input
              type="text"
              id="track-title"
              name="track-title"
              class="w-full px-3 py-2 border border-border rounded-md bg-input text-foreground"
            />
            <p id="track-exists-message" class="text-sm text-muted-foreground mt-1" style="display: none;">
              This track already exists. The title cannot be changed.
            </p>
          </div>
          <div class="flex justify-end gap-4">
            <Button type="button" id="cancel-add-track" variant="secondary">
              Cancel
            </Button>
            <Button type="submit" id="submit-add-track" disabled>
              Add Track
            </Button>
          </div>
        </form>
      </div>
    </div>
  );

  function render(container) {
    container.innerHTML = modalHtml;

    const urlInput = container.querySelector('#youtube-url');
    const trackInfo = container.querySelector('#track-info');
    const trackTitleInput = container.querySelector('#track-title');
    const trackExistsMessage = container.querySelector('#track-exists-message');
    const submitButton = container.querySelector('#submit-add-track');

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        cleanupAndClose();
      }
    };

    const cleanupAndClose = () => {
      window.removeEventListener('keydown', handleKeyDown);
      onClose();
    };

    window.addEventListener('keydown', handleKeyDown);

    container.querySelector('#cancel-add-track').onclick = () => {
      cleanupAndClose();
    };

        container.querySelector('#add-track-form').onsubmit = (e) => {
          e.preventDefault();
          const url = urlInput.value;
          const title = trackTitleInput.value;
          const submitButton = container.querySelector('#submit-add-track');
          const originalButtonContent = submitButton.innerHTML;
          submitButton.disabled = true;
          submitButton.innerHTML = `
            <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Adding...`;

          new TrackRepository().create(playlistId, url, title)
            .then(newTrack => {
              onTrackAdded(newTrack);
              cleanupAndClose();
            })
            .catch(err => {
              console.error("Error adding track:", err);
            })
            .finally(() => {
              submitButton.disabled = false;
              submitButton.innerHTML = originalButtonContent;
            });
        };
    let debounceTimer;
    urlInput.addEventListener('keyup', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            handleUrlInputChange(e.target.value);
        }, 500);
    });

    async function handleUrlInputChange(url) {
      if (!isYoutubeUrl(url)) {
        trackInfo.style.display = 'none';
        submitButton.disabled = true;
        return;
      }

      submitButton.disabled = false;

      try {
        // First, check if the track exists in our DB
        const existingTrack = await new TrackRepository().getByUrl(url);
        trackInfo.style.display = 'block';
        trackTitleInput.value = existingTrack.title;
        trackTitleInput.disabled = true;
        trackExistsMessage.style.display = 'block';
      } catch (error) {
        // If it doesn't exist, fetch title from YouTube oEmbed
        trackTitleInput.disabled = false;
        trackExistsMessage.style.display = 'none';
        try {
            const response = await fetch(`https://www.youtube.com/oembed?url=${url}&format=json`);
            if (!response.ok) throw new Error('Failed to fetch from oEmbed');
            const data = await response.json();
            trackInfo.style.display = 'block';
            trackTitleInput.value = data.title;
        } catch (oembedError) {
            console.error('oEmbed fetch error:', oembedError);
            trackInfo.style.display = 'none';
            submitButton.disabled = true;
        }
      }
    }

    function isYoutubeUrl(url) {
        var p = /^(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((\w|-){11})(?:\S+)?$/;
        return url.match(p);
    }
  }

  return { render };
}


export function ShareModal({ playlistId, isOwnerOrAdmin, onClose }) {
  const modalHtml = (
      <div id="share-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
        <div class="bg-neutral-900 border border-border rounded-lg p-8 max-w-md w-full flex flex-col gap-5">
          <div class="flex items-center justify-between">
            <h2 class="text-2xl font-bold text-foreground">Share Playlist</h2>
            <button id="cancel-share" class="text-muted-foreground hover:text-white transition-colors">✕</button>
          </div>

          {isOwnerOrAdmin && (
              <form id="share-form" class="flex flex-col gap-3">
                <Input label="Email address" placeholder="vincent.berry@umontpellier.fr" id="email"/>
                <Input label="Is Editor ?" id="editor" type="checkbox"/>
                <div class="flex justify-end gap-4">
                  <Button type="submit" id="submit-share" disabled>Share</Button>
                </div>
              </form>
          )}

          <div class="flex flex-col gap-2">
            <p class="text-sm font-semibold text-muted-foreground uppercase tracking-wider">People with access</p>
            <div id="shared-users-list" class="flex flex-col gap-2 max-h-64 overflow-y-auto">
              <p class="text-sm text-muted-foreground">Loading...</p>
            </div>
          </div>
        </div>
      </div>
  );

  function render(container) {
    container.innerHTML = modalHtml;

    const usersList = container.querySelector('#shared-users-list');
    const playlistRepo = new PlaylistRepository();

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') cleanupAndClose();
    };

    const cleanupAndClose = () => {
      window.removeEventListener('keydown', handleKeyDown);
      onClose();
    };

    window.addEventListener('keydown', handleKeyDown);
    container.querySelector('#cancel-share').onclick = () => cleanupAndClose();

    const loadUsers = async () => {
      try {
        const users = await playlistRepo.sharedWith(playlistId);

        if (users.length === 0) {
          usersList.innerHTML = `<p class="text-sm text-muted-foreground">No users have access yet.</p>`;
          return;
        }

        usersList.innerHTML = users.map((u) => `
          <div class="flex items-center justify-between gap-3 px-3 py-2 rounded-lg bg-white/5 border border-white/8" data-user-id="${u.idUser}">
            <div class="flex items-center gap-3 min-w-0">
              <div class="flex items-center justify-center w-9 h-9 rounded-full bg-neutral-700 text-sm font-semibold text-white shrink-0">
                ${u.username.charAt(0).toUpperCase()}
              </div>
              <div class="min-w-0">
                <p class="text-sm font-medium text-white truncate">${u.username}</p>
                <p class="text-xs text-muted-foreground truncate">${u.email}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              ${u.editor
            ? `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-400 border border-amber-500/20">Editor</span>`
            : `<span class="px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-500/15 text-blue-400 border border-blue-500/20">Viewer</span>`
        }
              ${isOwnerOrAdmin
            ? `<button class="remove-user flex items-center justify-center w-7 h-7 rounded-lg text-red-400 hover:bg-red-500/10 transition-colors" data-user-id="${u.idUser}">✕</button>`
            : ''
        }
            </div>
          </div>
        `).join('');

        if (isOwnerOrAdmin) {
          usersList.querySelectorAll('.remove-user').forEach((btn) => {
            btn.addEventListener('click', async () => {
              const userId = Number(btn.getAttribute('data-user-id'));
              btn.disabled = true;

              try {
                await playlistRepo.removeSharedUser(playlistId, userId);
                const row = usersList.querySelector(`[data-user-id="${userId}"]`);
                row?.remove();
                if (usersList.children.length === 0) {
                  usersList.innerHTML = `<p class="text-sm text-muted-foreground">No users have access yet.</p>`;
                }
                new AlertManager().success("User removed successfully");
              } catch {
                new AlertManager().error("Failed to remove user");
                btn.disabled = false;
              }
            });
          });
        }

      } catch {
        usersList.innerHTML = `<p class="text-sm text-red-400">Failed to load users.</p>`;
      }
    };

    loadUsers();

    if (isOwnerOrAdmin) {
      const emailInput = container.querySelector('#email');
      const editorInput = container.querySelector('#editor');
      const submitButton = container.querySelector('#submit-share');

      let debounceTimer;
      emailInput.addEventListener('keyup', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          submitButton.disabled = !isValidEmail(e.target.value);
        }, 300);
      });

      container.querySelector('#share-form').onsubmit = async (e) => {
        e.preventDefault();
        const email = emailInput.value;
        const editor = editorInput.checked;
        const originalContent = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = `
          <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Sharing...`;

        try {
          const response = await new TrackRepository().share(playlistId, email, editor);
          if (response == 200) {
            new AlertManager().success("Playlist shared successfully");
            emailInput.value = '';
            editorInput.checked = false;
            submitButton.disabled = true;
            await loadUsers();
            return;
          }
          throw new Error("Failed to share playlist");
        } catch {
          new AlertManager().error("Failed to share playlist");
        } finally {
          submitButton.disabled = false;
          submitButton.innerHTML = originalContent;
        }
      };
    }
  }

  return { render };
}
