import { createText, createButton } from "../components/generics/index";
import { secondsToReadableTime } from "../components/utils";

export function renderPlaylistPage(container, playlist, trackPlayer, onBack) {
  if (!container) return;

  container.innerHTML = ""; // Clear the container

  const page = document.createElement("div");
  page.className = "";

  // Header
  const header = document.createElement("div");
  header.className = "flex items-center mb-8 gap-4";
  const backButton = createButton({
    textContent: "← Back",
    variant: "ghost",
    size: "sm",
  });
  backButton.addEventListener("click", onBack);

  header.appendChild(backButton);
  page.appendChild(header);

  // Playlist Info
  const playlistInfo = document.createElement("div");
  playlistInfo.className = "flex items-center gap-8 my-8";
  const playlistImage = document.createElement("img");
  playlistImage.src = playlist.image;
  playlistImage.className = "w-48 h-48 rounded-md object-cover";
  playlistInfo.appendChild(playlistImage);

  // TODO: Add upload cover button
  // Instructions for implementation:
  // 1. Import the utility: import { triggerCoverUpload } from '../utils/upload-cover';
  // 2. Create upload button (example below)
  // 3. Add click handler
  //
  // Example code:
  // const uploadButton = createButton({
  //   textContent: 'Upload Cover',
  //   variant: 'outline',
  //   size: 'sm'
  // });
  //
  // uploadButton.addEventListener('click', () => {
  //   triggerCoverUpload(
  //     playlist.idPlaylist,
  //     (newImageUrl) => {
  //       playlistImage.src = newImageUrl;
  //       console.log('Cover uploaded successfully');
  //     },
  //     (error) => {
  //       console.error('Upload failed:', error);
  //       alert('Upload failed: ' + error);
  //     }
  //   );
  // });
  //
  // playlistInfo.appendChild(uploadButton);

  const playlistDetails = document.createElement("div");
  const playlistTitle = createText({
    textContent: playlist.name,
    size: "4xl",
    className: "font-bold",
  });
  const playlistDescription = createText({
    textContent: playlist.description,
    size: "lg",
    className: "text-muted-foreground",
  });
  playlistDetails.appendChild(playlistTitle);
  playlistDetails.appendChild(playlistDescription);
  playlistInfo.appendChild(playlistDetails);
  page.appendChild(playlistInfo);

  // Track list
  const trackListContainer = document.createElement("div");
  trackListContainer.className = "flex flex-col gap-4";

  const trackListHeader = document.createElement("div");
  trackListHeader.className =
    "grid grid-cols-[2rem_1fr_1fr_4rem] gap-4 px-4 text-muted-foreground";
  const numHeader = createText({ textContent: "#" });
  const titleHeader = createText({ textContent: "Title" });
  const artistHeader = createText({ textContent: "Artist" });
  const durationHeader = createText({ textContent: "Time" });
  trackListHeader.append(numHeader, titleHeader, artistHeader, durationHeader);
  trackListContainer.appendChild(trackListHeader);

  const tracks = playlist.tracks || [];
  tracks.forEach((track, index) => {
    const trackRow = document.createElement("div");
    trackRow.className =
      "grid grid-cols-[2rem_1fr_1fr_4rem] items-center gap-4 px-4 py-2 rounded-md transition-colors duration-200 hover:bg-gray-800 cursor-pointer";

    trackRow.id = `track-${index}`;

    trackRow.addEventListener("click", () => {
      if (trackPlayer.playlist.idPlaylist !== playlist.idPlaylist) {
        trackPlayer.setPlaylist(playlist);
      }
      trackPlayer.playTrack(index);
    });

    const trackNumberContainer = document.createElement("div");
    trackNumberContainer.className = "relative";

    const trackNumber = createText({ textContent: `${index + 1}` });
    trackNumber.classList.add("track-number");

    const playingIcon = document.createElement("img");
    playingIcon.src = new URL(
      "../assets/icons/pause.svg",
      import.meta.url,
    ).href;
    playingIcon.className = "playing-icon hidden w-4 h-4";

    trackNumberContainer.append(trackNumber, playingIcon);

    const trackTitle = createText({
      textContent: track.title,
      className: "font-medium track-title",
    });

    let artistTextContext = "";
    for (let i = 0; i < track.artists.length; i++) {
      artistTextContext += track.artists[i].name;
      if (i < track.artists.length - 1) {
        artistTextContext += ", ";
      }
    }

    const trackArtist = createText({
      textContent: artistTextContext ?? "Unknown",
    });
    const trackDuration = createText({
      textContent: secondsToReadableTime(track.durationSeconds),
    });

    trackRow.append(
      trackNumberContainer,
      trackTitle,
      trackArtist,
      trackDuration,
    );
    trackListContainer.appendChild(trackRow);
  });

  page.appendChild(trackListContainer);

  container.appendChild(page);
}
