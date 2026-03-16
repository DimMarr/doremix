import enum


class PlaylistVisibility(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    OPEN = "OPEN"


class Actions(str, enum.Enum):
    CREATE = "CREATE"
    READ = "READ"
    EDIT = "EDIT"
    DELETE = "DELETE"
    BAN = "BAN"
    PROMOTE = "PROMOTE"
    DEMOTE = "DEMOTE"
    SHARE = "SHARE"
    SEARCH = "SEARCH"


class Ressources(str, enum.Enum):
    PLAYLIST = "PLAYLIST"
    PLAYLIST_PUBLIC = "PLAYLIST_PUBLIC"
    PLAYLIST_PRIVATE = "PLAYLIST_PRIVATE"
    PLAYLIST_SHARED = "PLAYLIST_SHARED"
    USER = "USER"
    GENRE = "GENRE"
