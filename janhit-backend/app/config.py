from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./janhit.db"
    ENV: str = "development"
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"


settings = Settings()
