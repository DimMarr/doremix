import { TrackRepository } from "@repositories/trackRepository";
import { Button } from "@components/generics";
import { AlertManager } from "@utils/AlertManager";

export function AddTrackModal({ playlistId, onClose, onTrackAdded }) {
  const modalHtml = (
    <div id="add-track-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-md w-full">
        <h2 class="text-2xl font-bold mb-4">Add New Track</h2>
        <form id="add-track-form">
          <div class="mb-4">
            <label for="youtube-url" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              YouTube URL
            </label>
            <input
              type="text"
              id="youtube-url"
              name="youtube-url"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="https://www.youtube.com/watch?v=..."
            />
          </div>
          <div id="track-info" class="mb-4" style="display: none;">
            <label for="track-title" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Track Title
            </label>
            <input
              type="text"
              id="track-title"
              name="track-title"
              class="w-full px-3 py-2 border border-gray-300 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <p id="track-exists-message" class="text-sm text-gray-500 mt-1" style="display: none;">
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

          TrackRepository.addTrackByUrl(playlistId, url, title)
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
        const existingTrack = await TrackRepository.getTrackByUrl(url);
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
