from typing import List, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and configuration.
    Loads settings from environment variables and .env file.
    Provides type-validated configuration for the application.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Process Management API"
    ENV: str = "development"

    # CORS
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:8000",
        "http://localhost:3000",
    ]

    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    POSTGRES_PORT: str = "5432"  # This is coming in as a string from environment variables
    DATABASE_URI: Union[PostgresDsn, None] = None

    @field_validator("POSTGRES_PORT")
    def validate_postgres_port(cls, v):
        """Convert string port to integer for validation"""
        return int(v)

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Return the database URL as a string for SQLAlchemy.
        Constructs a connection string from component parts.
        """
        db_uri = PostgresDsn.build(
            scheme="postgresql+asyncpg",  # Using asyncpg driver for async SQLAlchemy
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=int(self.POSTGRES_PORT),
            path=f"{self.POSTGRES_DB}",
        )
        return str(db_uri)

    @property
    def SQLALCHEMY_SYNCDATABASE_URI(self) -> str:
        """
        Return the database URL as a string for SQLAlchemy.
        Constructs a connection string from component parts.
        """
        db_uri = PostgresDsn.build(
            scheme="postgresql",  # Using asyncpg driver for async SQLAlchemy
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=int(self.POSTGRES_PORT),
            path=f"{self.POSTGRES_DB}",
        )
        return str(db_uri)

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Union[str, None], values) -> Union[str, None]:
        """
        Validate and construct the database URI if not provided directly.
        If a string is provided, it's returned as is; otherwise, built from components.
        """
        if isinstance(v, str):
            return v

        # Convert PostgresDsn to string to match the return type
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",  # Using asyncpg driver for async SQLAlchemy
                username=values.data.get("POSTGRES_USER"),
                password=values.data.get("POSTGRES_PASSWORD"),
                host=values.data.get("POSTGRES_SERVER"),
                port=values.data.get("POSTGRES_PORT"),
                path=f"{values.data.get('POSTGRES_DB') or ''}",
            )
        )


settings = Settings()
