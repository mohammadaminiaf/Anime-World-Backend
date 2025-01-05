from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, engine
from app.routers import movies, auth


app = FastAPI(title="Anime World")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the uploads directory to serve uploaded files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(movies.router, tags=["Movies"])
app.include_router(auth.router, tags=["Auth"])


@app.get("/")
def road_root():
    return {"message": "Welcome to Anime World!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="10.0.2.2", port=8000, reload=True)
