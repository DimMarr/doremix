from enum import Enum

class Visibility(str, Enum):
    PRIVATE = "PRIVATE"
    OPEN = "OPEN"
    PUBLIC = "PUBLIC"
    SHARED = "SHARED"