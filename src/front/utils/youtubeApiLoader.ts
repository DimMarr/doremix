/**
 * Waits for the YouTube IFrame API to load and be ready.
 * Loads the API script if not already loaded.
 * Returns a promise that resolves when the API is ready.
 */
export function waitForYouTubeAPI(): Promise<void> {
    return new Promise((resolve) => {
        // Check if API is already loaded
        if (window.YT && window.YT.Player) {
            resolve();
            return;
        }

        // Store the original onYouTubeIframeAPIReady if it exists
        const originalCallback = (window as any).onYouTubeIframeAPIReady;

        // Define the callback that YouTube calls when API is ready
        (window as any).onYouTubeIframeAPIReady = () => {
            // Call original callback if it existed
            if (originalCallback && typeof originalCallback === 'function') {
                originalCallback();
            }
            // Resolve our promise
            resolve();
        };

        // Load the YouTube API script if not already loading/loaded
        if (!document.querySelector('script[src*="youtube.com/iframe_api"]')) {
            const tag = document.createElement('script');
            tag.src = 'https://www.youtube.com/iframe_api';
            const firstScriptTag = document.getElementsByTagName('script')[0];
            firstScriptTag.parentNode?.insertBefore(tag, firstScriptTag);
        }
    });
}
