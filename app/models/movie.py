from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base
import uuid
from sqlalchemy import Column, Text, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genre = Column(String)
    rating = Column(Float)

