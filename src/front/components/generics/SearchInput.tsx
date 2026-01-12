export interface SearchInputProps {
    placeholder?: string;
    className?: string;
}

export function SearchInput({
    placeholder = "Search tracks and playlists...",
    className = ""
}: SearchInputProps) {
    return (
        <div class={`relative w-full max-w-2xl mx-auto ${className}`}>
            <input
                type="text"
                placeholder={placeholder}
                class="w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                id="search-input"
            />
        </div>
    );
}
