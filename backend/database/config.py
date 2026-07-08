from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql://postgres:postgres123@localhost:5432/ledger_db"
    )

    class Config:
        env_file = ".env"


settings = Settings()