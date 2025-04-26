from typing import List, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Process Management API"
    
    # CORS
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["http://localhost:8000", "http://localhost:3000"]
    
    # PostgreSQL
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str  # This is coming in as a string from environment variables
    DATABASE_URI: Union[PostgresDsn, None] = None

    @field_validator("POSTGRES_PORT")
    def validate_postgres_port(cls, v):
        # Convert string port to integer
        return int(v)

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=int(self.POSTGRES_PORT),  # Convert to int here
            path=f"/{self.POSTGRES_DB}"
        )

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Union[str, None], values) -> Union[str, None]:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data.get("POSTGRES_USER"),
            password=values.data.get("POSTGRES_PASSWORD"),
            host=values.data.get("POSTGRES_SERVER"),
            port=values.data.get("POSTGRES_PORT"),
            path=f"{values.data.get('POSTGRES_DB') or ''}",
        )


settings = Settings() 