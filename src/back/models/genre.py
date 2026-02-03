from sqlalchemy import Column, Integer, String
from back.database import Base


class Genre(Base):
    __tablename__ = "genre"

    idGenre = Column("idgenre", Integer, primary_key=True, index=True)
    label = Column("label", String(255), nullable=False)
