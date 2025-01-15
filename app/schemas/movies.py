from pydantic import BaseModel
from typing import Optional, List
from fastapi import Form, File

class MovieBase(BaseModel):
    title: str
    genres: str
    rating: float
    
    class Config:
        orm_mode = True
    
class MovieSchema(MovieBase):
    id: int
    title: str
    english_title: Optional[str] = None
    image_url: Optional[str] = None
    genres: Optional[List[str]] = None
    rating: Optional[float] = None
    
    class Config:
        from_attributes=True
        orm_mode = True
    

class Movie(MovieBase):
    id: int
    
    class Config:
        orm_mode = True
