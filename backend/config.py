from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

from constants import Environment

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    Pydantic automatically reads the .env file and validates the types.
    """
    # Application Config
    environment: Environment = Environment.DEVELOPMENT
    backend_port: int = 8000  # Default to 8000 if not found in .env
    frontend_port: int = 5173

    # Database Config
    postgres_user: str
    postgres_password: str
    postgres_db: str
    database_url: str | None = None

    pool_size: int = 5
    max_overflow: int = 10

    # AI Config
    gemini_api_key: str
    db_encryption_key: str

    # Read from the local .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore"
    )

    def get_database_url(self) -> str:
        """Construct the DB URL if it wasn't explicitly provided."""
        if self.database_url:
            return self.database_url
        return URL.create(
            drivername="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host="db",
            port=5432,
            database=self.postgres_db
        )

# Instantiate as a singleton so it is loaded into memory exactly once
settings = Settings()
