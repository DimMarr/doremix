from sqlalchemy import Column, Integer, ForeignKey, Boolean
from database import Base

class UserPlaylist(Base):
    __tablename__ = "user_playlist"
    
    idUser = Column(Integer, ForeignKey("users.idUser", ondelete="CASCADE"), primary_key=True)
    idPlaylist = Column(Integer, ForeignKey("playlist.idPlaylist", ondelete="CASCADE"), primary_key=True)
    editor = Column(Boolean, default=False)