from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import database
from app.models import movie
from app.schemas import movies

router = APIRouter()

@router.get('/', response_model=movies.Movie)
def read_movies(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return db.query(movie.Movie).offset(skip).limit(limit).all()


@router.post('/', response_model=movies.Movie)
def create_movie(movie: movies.Movie, db: Session = Depends(database.get_db)):
    db_movie = movie.Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie
        
