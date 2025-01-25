from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Anime World"
    database_url: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
