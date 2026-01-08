export interface SearchInputProps {
    placeholder?: string;
    onSearch: (query: string) => void;
    className?: string;
}

export function createSearchInput(props: SearchInputProps): HTMLDivElement {
    const { placeholder = "Search tracks and playlists...", onSearch, className = "" } = props;

    const container = document.createElement("div");
    container.className = `relative w-full max-w-2xl mx-auto ${className}`;

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = placeholder;
    input.className = "w-full px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500";

    let debounceTimer: ReturnType<typeof setTimeout>;

    input.addEventListener("input", (e) => {
        const target = e.target as HTMLInputElement;
        const query = target.value.trim();


        clearTimeout(debounceTimer);


        if (query.length < 2) {
            onSearch("");
            return;
        }

        // Wait 300ms before searching
        debounceTimer = setTimeout(() => {
            onSearch(query);
        }, 300);
    });

    container.appendChild(input);
    return container;
}
