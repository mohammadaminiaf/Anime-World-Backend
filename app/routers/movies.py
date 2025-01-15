from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import favorite_movie, viewed_movie
from app.schemas import movies
from app.schemas.users import Token
from typing import List
from app.utils.auth import get_current_user

router = APIRouter(prefix="/movies", tags=["movies"])


# Get all movies
@router.get("/", response_model=Token)
def read_movies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    all_movies = db.query(favorite_movie.FavoriteMovie).offset(skip).limit(limit).all()
    return {}


# Get all favorite movies
@router.get("/favorite", response_model=Token)
def get_all_favorite_movies(
    page_num: int = 0,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    if not user_id:
        raise HTTPException(
            status_code=403, detail="Unauthenticated! You can get this list of movies"
        )
        
    # Query favorite movies with pagination
    offset = (page_num - 1) * page_size
    all_movies = db.query(favorite_movie.FavoriteMovie).offset(offset).limit(page_size).all()

    # Transform data to match the Pydantic schema
    response = [movies.MovieSchema.from_orm(movie) for movie in all_movies]
    
    total_count = db.query(favorite_movie.FavoriteMovie).count()
    last_page = -(-total_count // page_size)

    return {
        "data": {
            "data": response,
            'page_num': page_num,
            'last_page': last_page,
            'page_size': page_size,
            'total_count': total_count,
        },
        "access_token": None,
        "token_type": "bearer",
        "status_code": 200,
        "message": "Successfully fetched favorite movies.",
    }


# This route is used to add a movie to list of favorite movies
@router.post("/favorite", response_model=Token)
def create_favorite_movie(
    movie: movies.MovieSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    if not user_id:
        raise HTTPException(
            status_code=403, detail="You don't have permission to add this movie"
        )

    # Check if the movie already exists
    existing_movie = (
        db.query(favorite_movie.FavoriteMovie)
        .filter(favorite_movie.FavoriteMovie.id == movie.id)
        .first()
    )

    if existing_movie:
        raise HTTPException(status_code=409, detail="Movie is already a favorite")

    # Create a database movie object
    db_movie = favorite_movie.FavoriteMovie(**movie.model_dump())
    db_movie.user_id = user_id

    # Add movie to the database
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)

    return {
        "data": db_movie.to_dict(),
        "access_token": None,
        "token_type": "bearer",
        "status_code": 200,
        "message": "Movie was successfully added to the favorites.",
    }


# This route is used to delete a movie from list of favorite movies
@router.delete("/favorite/{movie_id}", response_model=Token)
def delete_favorite(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Check if the movie already exists in the favorites
    existing_movie = (
        db.query(favorite_movie.FavoriteMovie)
        .filter(favorite_movie.FavoriteMovie.id == movie_id)
        .first()
    )

    if existing_movie.user_id != current_user["id"]:
        raise HTTPException(
            status_code=403, detail="You don't have permission to delete this movie"
        )

    if existing_movie:
        # If the movie exists, remove it from favorites
        db.delete(existing_movie)
        db.commit()
        return {
            "data": {"id": existing_movie.id},
            "access_token": None,
            "token_type": "bearer",
            "status_code": 200,
            "message": "Movie was successfully removed from the favorites.",
        }
        
    else:
        raise HTTPException(
            status_code=400,
            detail="The movie does not exist in the database",
        )


# This route add a movie to the table of viewed movies
@router.post("/viewed", response_model=Token)
def create_viewed_movie(
    movie: movies.MovieSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["id"]
    if not user_id:
        raise HTTPException(
            status_code=403, detail="You don't have permission to add this movie as viewed"
        )

    # Check if the movie already exists
    existing_movie = (
        db.query(viewed_movie.ViewedMovie)
        .filter(viewed_movie.ViewedMovie.id == movie.id)
        .first()
    )
    
    if existing_movie:
        return {
            "data": None,
            "access_token": None,
            "token_type": "bearer",
            "status_code": 200,
            "message": "Movie is already viewed by user.",
        }

    if not existing_movie:
        # Create a database movie object
        db_movie = viewed_movie.ViewedMovie(**movie.model_dump())
        db_movie.user_id = user_id

        # Add movie to the database
        db.add(db_movie)
        db.commit()
        db.refresh(db_movie)
        
        return {
            "data": db_movie.to_dict(),
            "access_token": None,
            "token_type": "bearer",
            "status_code": 200,
            "message": "Movie was successfully added to the viewed movies.",
        }
