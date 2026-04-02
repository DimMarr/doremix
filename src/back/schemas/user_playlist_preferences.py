from pydantic import BaseModel, field_validator
from typing import Optional, List

VALID_SORT_MODES = {"date_desc", "name_asc", "custom"}


class PlaylistPreferencesSchema(BaseModel):
    sort_mode: str
    custom_order: Optional[List[int]] = None


class PlaylistPreferencesUpdate(BaseModel):
    sort_mode: str
    custom_order: Optional[List[int]] = None

    @field_validator("sort_mode")
    @classmethod
    def validate_sort_mode(cls, v: str) -> str:
        if v not in VALID_SORT_MODES:
            raise ValueError(f"sort_mode must be one of {VALID_SORT_MODES}")
        return v
