import { SearchRepository } from "@repositories/index";
import { SearchResults } from "./searchResults";
import { trackPlayerInstance } from "@layouts/mainLayout";

export interface SearchBarProps {
    placeholder?: string;
    className?: string; // Classes for the container (bg, rounded, size, etc.)
    inputClassName?: string; // Classes for the input (text color, placeholder color)
}

export function SearchBar({
    placeholder = "Search tracks and playlists...",
    className = "",
    inputClassName = ""
}: SearchBarProps) {
    return (
        <div class={`relative w-full max-w-2xl mx-auto flex items-center group transition-all duration-200 z-50 ${className}`}>
            <svg
                class="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-current opacity-70 pointer-events-none"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
            >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
            </svg>
            <input
                type="text"
                placeholder={placeholder}
                class={`flex h-full w-full bg-transparent border-none px-12 py-2 text-sm focus:outline-none focus:ring-0 disabled:cursor-not-allowed disabled:opacity-50 transition-colors ${inputClassName}`}
                id="search-input"
            />
        </div>
    );
}

function removeExistingResults(searchSection: HTMLElement | null): void {
    const existingResults = searchSection?.querySelector('[class*="absolute top-full"]');
    if (existingResults) {
        existingResults.remove();
    }
}

function renderSearchResults(
    searchContainer: Element,
    results: { tracks: any[], playlists: any[] }
): void {
    const resultsHtml = SearchResults({
        tracks: results.tracks,
        playlists: results.playlists,
    });

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = resultsHtml;
    searchContainer.appendChild(tempDiv.firstElementChild!);
}

function attachTrackClickHandlers(
    searchContainer: Element,
    searchSection: HTMLElement | null,
    getCurrentResults: () => { tracks: any[], playlists: any[] } | null,
    clearResults: () => void
): void {
    const trackItems = searchContainer.querySelectorAll('[data-track-index]');
    trackItems.forEach((item) => {
        const index = parseInt((item as HTMLElement).dataset.trackIndex || '0', 10);
        item.addEventListener('click', () => {
            const currentResults = getCurrentResults();
            if (currentResults) {
                trackPlayerInstance.playSingleTrack(currentResults.tracks[index]);
            }
            removeExistingResults(searchSection);
            clearResults();
        });
    });
}

function attachPlaylistClickHandlers(
    searchContainer: Element,
    searchSection: HTMLElement | null,
    getCurrentResults: () => { tracks: any[], playlists: any[] } | null,
    clearResults: () => void
): void {
    const playlistItems = searchContainer.querySelectorAll('[data-playlist-index]');
    playlistItems.forEach((item) => {
        item.addEventListener('click', () => {
            // let the router handle navigation
            removeExistingResults(searchSection);
            clearResults();
        });
    });
}

async function performSearch(
    query: string,
    searchSection: HTMLElement | null,
    setResults: (results: { tracks: any[], playlists: any[] }) => void,
    getCurrentResults: () => { tracks: any[], playlists: any[] } | null,
    clearResults: () => void
): Promise<void> {
    const results = await new SearchRepository().search(query);
    setResults(results);

    const searchContainer = searchSection?.querySelector('[class*="relative w-full"]');
    if (searchContainer) {
        renderSearchResults(searchContainer, results);
        attachTrackClickHandlers(searchContainer, searchSection, getCurrentResults, clearResults);
        attachPlaylistClickHandlers(searchContainer, searchSection, getCurrentResults, clearResults);
    }
}

function handleSearchInput(
    searchSection: HTMLElement | null,
    getDebounceTimer: () => ReturnType<typeof setTimeout> | undefined,
    setDebounceTimer: (timer: ReturnType<typeof setTimeout>) => void,
    setResults: (results: { tracks: any[], playlists: any[] } | null) => void,
    getCurrentResults: () => { tracks: any[], playlists: any[] } | null
): (e: Event) => void {

    return (e: Event) => {
        const target = e.target as HTMLInputElement;
        const query = target.value.trim();

        // Initialisation du timer.
        const currentTimer = getDebounceTimer();
        if (currentTimer) {
            clearTimeout(currentTimer);
        }

        // Remove les résultats de la recherche existants.
        removeExistingResults(searchSection);

        // On commence la recherche quand il y a au moins 3 caractères dans la recherche.
        if (query.length < 2) {
            setResults(null);
            return;
        }

        // On effectue la recherche avec du débounce
        const timer = setTimeout(() => {
            performSearch(
                query,
                searchSection,
                setResults,
                getCurrentResults,
                () => setResults(null)
            );
        }, 300);
        setDebounceTimer(timer);
    };
}

export function initSearchBar() {
    let currentResults: { tracks: any[], playlists: any[] } | null = null;
    let debounceTimer: ReturnType<typeof setTimeout> | undefined;
    const searchSection = document.getElementById("searchSection");

    const getDebounceTimer = () => debounceTimer;
    const setDebounceTimer = (timer: ReturnType<typeof setTimeout>) => { debounceTimer = timer; };
    const setResults = (results: { tracks: any[], playlists: any[] } | null) => { currentResults = results; };
    const getCurrentResults = () => currentResults;

    // On ajoute un listener sur la barre de recherche pour effectuer une recherche lorsque qu'un utilisateur tape dans la barre de recherche.
    const searchInputElement = document.getElementById("search-input") as HTMLInputElement;
    if (searchInputElement) {
        searchInputElement.addEventListener(
            "input",
            handleSearchInput(
                searchSection,
                getDebounceTimer,
                setDebounceTimer,
                setResults,
                getCurrentResults
            )
        );
    }
    document.addEventListener('click', (e) => {
        const searchContainer = searchSection?.querySelector('[class*="relative w-full"]');
        const target = e.target as Node;

        if (searchContainer && !searchContainer.contains(target)) {
            removeExistingResults(searchSection);
            setResults(null);
        }
    });
}
