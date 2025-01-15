from sqlalchemy import Column, Integer, String, Float
from app.db.database import Base
import uuid
from sqlalchemy import Column, Text, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


# Database User
class UserDB(Base):
    __tablename__ = "users"
    id = Column(
        String(36),
        primary_key=True,
        unique=True,
        nullable=False,
        default=str(uuid.uuid4()),
    )
    name = Column(String, nullable=False)
    username = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    password = Column(Text, nullable=False)
    is_authenticated = Column(Boolean, default=False)

    # Add the relationship to FavoriteMovie
    favorite_movies = relationship(
        "FavoriteMovie",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    viewed_movies = relationship(
        'ViewedMovie',
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Relationships to ProductsDB and UserImagesDB
    profile_photo = relationship(
        "UserImagesDB",
        cascade="all, delete-orphan",
        back_populates="user",
        uselist=False,
    )
    # products = relationship(
    #     "ProductsDB", cascade="all, delete-orphan", back_populates="user"
    # )

    def to_dict(self):
        user_data = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name != "password"
        }
        if self.profile_photo:
            user_data["profile_photo"] = self.profile_photo.image_url
        return user_data


# User Images DB
class UserImagesDB(Base):
    __tablename__ = "user_images"
    id = Column(
        String[36],
        primary_key=True,
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    user_id = Column(String[36], ForeignKey("users.id"), nullable=False)
    image_url = Column(String(255), nullable=False)

    # Define the relationship
    user = relationship("UserDB", back_populates="profile_photo")
