from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://prospector:prospector@db:5432/prospector"
    google_places_api_key: str | None = None
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    class Config:
        env_file = ".env"


settings = Settings()
