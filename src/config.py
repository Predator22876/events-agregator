from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    EVENTS_PROVIDER_URL: str
    EVENTS_PROVIDER_API_KEY: str

    POSTGRES_DATABASE_NAME: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE_NAME}"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[1] / ".env"),
        env_file_encoding="utf-8-sig",
        extra="ignore",
    )


settings = Settings()
print(settings)
