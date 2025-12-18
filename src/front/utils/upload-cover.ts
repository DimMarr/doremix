import { uploadPlaylistCover, getCoverImageUrl } from '../services/api';


export async function handleCoverUpload(
    playlistId: number,
    imageFile: File,
    onSuccess: (imageUrl: string, updatedPlaylist: any) => void,
    onError: (error: string) => void
): Promise<void> {
    try {

        if (!imageFile.type.startsWith('image/')) {
            throw new Error('File must be an image');
        }

        if (imageFile.size > 5 * 1024 * 1024) {
            throw new Error('Image must be less than 5MB');
        }


        const updatedPlaylist = await uploadPlaylistCover(playlistId, imageFile);


        const imageUrl = getCoverImageUrl(updatedPlaylist.coverImage);


        if (imageUrl) {
            onSuccess(imageUrl, updatedPlaylist);
        } else {
            throw new Error('No cover image returned');
        }
    } catch (error) {
        onError(error instanceof Error ? error.message : 'Upload failed');
    }
}

export function triggerCoverUpload(
    playlistId: number,
    onSuccess: (imageUrl: string) => void,
    onError: (error: string) => void
): void {

    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';

    fileInput.addEventListener('change', async (e: Event) => {
        const target = e.target as HTMLInputElement;
        const file = target.files?.[0];
        if (file) {
            await handleCoverUpload(playlistId, file, onSuccess, onError);
        }
    });

    fileInput.click();
}
