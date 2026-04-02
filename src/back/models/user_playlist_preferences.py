from sqlalchemy import Column, Integer, String
# Using sqlalchemy.types.JSON (not JSONB) to remain compatible with the
# SQLite in-memory test database; SQLAlchemy maps JSON -> JSONB on PostgreSQL.
from sqlalchemy.types import JSON
from database import Base


class UserPlaylistPreferences(Base):
    __tablename__ = "user_playlist_preferences"

    idUser = Column("iduser", Integer, primary_key=True, nullable=False)
    sort_mode = Column(
        "sort_mode", String(20), nullable=False, default="date_desc"
    )
    # Ordered list of idPlaylist integers. NULL when sort_mode != 'custom'.
    custom_order = Column("custom_order", JSON, nullable=True)
