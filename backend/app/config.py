from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "ApplyWise AI Live"
    database_url: str = "sqlite:///./applywise.db"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    openai_api_key: str | None = None
    # Keep scraping polite and transparent
    user_agent: str = "ApplyWiseAI/1.0 job matching assistant (human-reviewed applications)"

    class Config:
        env_file = ".env"

settings = Settings()
