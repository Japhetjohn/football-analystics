from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    bot_token: str = "TBD"
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "football_analytics"
    redis_url: str = "redis://localhost:6379/0"
    
    api_football_key: str = "TBD"

    @property
    def database_url(self) -> str:
        return "sqlite+aiosqlite:///test.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
