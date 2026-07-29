from collections.abc import Generator
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Settings(BaseSettings):
    app_name: str = "Chess Analytics"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    chess_username: str = "mazapander0"
    chess_api_base_url: str = "https://api.chess.com/pub"
    chess_user_agent: str = "ChessAnalytics/0.1 (personal project)"
    database_url: str = "postgresql+psycopg://chess:chess@postgres:5432/chess_analytics"
    sql_echo: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
engine = create_engine(settings.database_url, echo=settings.sql_echo, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
