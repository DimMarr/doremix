import { PlaylistRepository, TrackRepository } from "@repositories/index";
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


export function ShareModal({ playlistId, onClose }) {
  const modalHtml = (
    <div id="share-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-neutral-900 border border-border rounded-lg p-8 max-w-md w-full flex flex-col gap-5">
        <h2 class="text-2xl font-bold text-foreground mb-4">Share Playlist</h2>

        <div class="flex gap-2 border-b border-border mb-2">
          <button id="tab-share" class="tab-btn pb-2 px-1 text-sm font-medium border-b-2 border-primary text-primary transition-colors">
            Share
          </button>
          <button id="tab-transfer" class="tab-btn pb-2 px-1 text-sm font-medium border-b-2 border-transparent text-muted-foreground hover:text-foreground transition-colors">
            Transfer ownership
          </button>
        </div>

        <div id="panel-share">
          <form id="share-form" class="flex flex-col gap-5">
            <div class="flex flex-col gap-5">
              <Input label="Email address" placeholder="vincent.berry@umontpellier.fr" id="email"/>
              <Input label="Is Editor?" id="editor" type="checkbox"/>
            </div>
            <div class="flex justify-end gap-4">
              <Button type="button" id="cancel-share" variant="secondary">Cancel</Button>
              <Button type="submit" id="submit-share" disabled>Share</Button>
            </div>
          </form>
        </div>

        <div id="panel-transfer" class="hidden flex flex-col gap-5">
          <p class="text-sm text-muted-foreground">
            Transfer ownership to another user.<br></br>
            <span class="text-destructive font-medium">This action is irreversible, you will lose access to this playlist unless the new owner invites you back.</span>
          </p>
          <form id="transfer-form" class="flex flex-col gap-5">
            <Input label="New owner email" placeholder="new.owner@umontpellier.fr" id="transfer-email"/>
            <div class="flex justify-end gap-4">
              <Button type="button" id="cancel-transfer" variant="secondary">Cancel</Button>
              <Button type="submit" id="submit-transfer" variant="destructive" disabled>Transfer</Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );

  function render(container) {
    container.innerHTML = modalHtml;

    const tabShare = container.querySelector('#tab-share');
    const tabTransfer = container.querySelector('#tab-transfer');
    const panelShare = container.querySelector('#panel-share');
    const panelTransfer = container.querySelector('#panel-transfer');

    function activateTab(tab) {
      const isShare = tab === 'share';
      tabShare.classList.toggle('border-primary', isShare);
      tabShare.classList.toggle('text-primary', isShare);
      tabShare.classList.toggle('border-transparent', !isShare);
      tabShare.classList.toggle('text-muted-foreground', !isShare);

      tabTransfer.classList.toggle('border-primary', !isShare);
      tabTransfer.classList.toggle('text-primary', !isShare);
      tabTransfer.classList.toggle('border-transparent', isShare);
      tabTransfer.classList.toggle('text-muted-foreground', isShare);

      panelShare.classList.toggle('hidden', !isShare);
      panelTransfer.classList.toggle('hidden', isShare);
    }

    tabShare.onclick = () => activateTab('share');
    tabTransfer.onclick = () => activateTab('transfer');

    const handleKeyDown = (e) => { if (e.key === 'Escape') cleanupAndClose(); };
    const cleanupAndClose = () => {
      window.removeEventListener('keydown', handleKeyDown);
      onClose();
    };
    window.addEventListener('keydown', handleKeyDown);

    const emailInput = container.querySelector('#email');
    const submitShare = container.querySelector('#submit-share');

    container.querySelector('#cancel-share').onclick = () => cleanupAndClose();

    let debounceTimer;
    emailInput.addEventListener('keyup', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        submitShare.disabled = !isValidEmail(e.target.value);
      }, 500);
    });

    container.querySelector('#share-form').onsubmit = async (e) => {
      e.preventDefault();
      const email = emailInput.value;
      const editor = container.querySelector('#editor').checked;
      const originalContent = submitShare.innerHTML;

      submitShare.disabled = true;

      try {
        const response = await new TrackRepository().share(playlistId, email, editor);
        if (response === 200) {
          new AlertManager().success('Playlist shared successfully');
          cleanupAndClose();
          return;
        }
        throw new Error();
      } catch {
        submitShare.disabled = false;
        submitShare.innerHTML = originalContent;
        new AlertManager().error('Error sharing playlist');
      }
    };

    const transferEmailInput = container.querySelector('#transfer-email');
    const submitTransfer = container.querySelector('#submit-transfer');

    container.querySelector('#cancel-transfer').onclick = () => cleanupAndClose();

    let transferDebounce;
    transferEmailInput.addEventListener('keyup', (e) => {
      clearTimeout(transferDebounce);
      transferDebounce = setTimeout(() => {
        submitTransfer.disabled = !isValidEmail(e.target.value);
      }, 500);
    });

    container.querySelector('#transfer-form').onsubmit = async (e) => {
      e.preventDefault();
      const email = transferEmailInput.value;
      const originalContent = submitTransfer.innerHTML;

      submitTransfer.disabled = true;

      try {
        const response = await new PlaylistRepository().transfer(playlistId, email);
        if (response === 200) {
          new AlertManager().success('Ownership transferred successfully');
          cleanupAndClose();
          return;
        }
        throw new Error();
      } catch {
        submitTransfer.disabled = false;
        submitTransfer.innerHTML = originalContent;
        new AlertManager().error('Error transferring ownership');
      }
    };
  }

  return { render };
}
