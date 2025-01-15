from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


# This model represents the table favorite movies, its job is to store all the movies you have added as your favorite
class FavoriteMovie(Base):
    __tablename__ = "favorite_movies"
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
        nullable=False,
    )
    title = Column(String, index=True)
    english_title = Column(String, nullable=True)
    image_url = Column(String)
    genres = Column(JSON, nullable=True)
    rating = Column(Float, nullable=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Define relationship with the UserDB table
    user = relationship("UserDB", back_populates="favorite_movies")
    
    def to_dict(self):
        movie_data = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        return movie_data
