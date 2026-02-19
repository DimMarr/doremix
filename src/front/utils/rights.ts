import { PlaylistRepository } from "@repositories/playlistRepository";
import { authService } from "./authentication";
import Playlist from "@models/playlist";

// True if is editor of a shared playlist, else false
export async function isEditor(repo: PlaylistRepository, playlist: Playlist) {
  const userInfos = await authService.infos();
  const currentUserId = userInfos.id

  const users = await repo.sharedWith(playlist.idPlaylist)
  const editors = users.filter(user => user.editor === true).map(user => user.idUser)
  return editors.includes(currentUserId)
}

// True if can edit (Owner, Editor, Admin), else false
export async function canEdit (repo: PlaylistRepository, playlist: Playlist) {
  const userInfos = await authService.infos();
  const currentUserRole = userInfos.role
  const currentUserId = userInfos.id

  const idOwner = playlist.idOwner
  if (currentUserId == idOwner){
    console.log("isOwner")
    return true
  }
  if (await isEditor(repo, playlist)){
    console.log("isEditor")
    return true
  }
  if (currentUserRole == "ADMIN"){
    console.log("isAdmin")
    return true
  }
  return false
}
