import enum


class PlaylistVisibility(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    OPEN = "OPEN"
