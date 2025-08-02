from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    ENV: str = Field(min_length=1, default="development")

    SECRET_KEY: str = Field(min_length=1)

    API_HOST: str = Field(min_length=1)
    API_PORT: int

    TCP_HOST: str = Field(min_length=1)
    TCP_PORT: int

    # Database - Microsoft SQL Server
    MSSQL_USER: str
    MSSQL_PASSWORD: str
    MSSQL_HOST: str
    MSSQL_PORT: str = "1433"
    MSSQL_DB: str
    MSSQL_DRIVER: str = Field(default="{ODBC Driver 17 for SQL Server}")

    # Database - PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"

    # External API settings
    EXTERNAL_API_TIMEOUT: int = 30
    EXTERNAL_API_RETRIES: int = 3

    TIME_ZONE: str = Field(default="Asia/Kuala_Lumpur")

    @property
    def DATABASE_URL(self) -> str:
        """Generates the SQLAlchemy database URL for MSSQL (async)"""
        if not self.MSSQL_USER:
            return f"mssql+aioodbc:///?odbc_connect=DRIVER={self.MSSQL_DRIVER};SERVER={self.MSSQL_HOST},{self.MSSQL_PORT};DATABASE={self.MSSQL_DB};trusted_connection=yes;"  # Windows Authentication Local Testing Use
        else:
            return f"mssql+aioodbc:///?odbc_connect=DRIVER={self.MSSQL_DRIVER};SERVER={self.MSSQL_HOST},{self.MSSQL_PORT};DATABASE={self.MSSQL_DB};UID={self.MSSQL_USER};PWD={self.MSSQL_PASSWORD};"

    @property
    def POSTGRES_DATABASE_URL(self) -> str:
        """Generates the SQLAlchemy database URL for PostgreSQL (async)"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_MASTER(self) -> str:
        if not self.MSSQL_USER:
            return f"mssql+aioodbc:///?odbc_connect=DRIVER={self.MSSQL_DRIVER};SERVER={self.MSSQL_HOST},{self.MSSQL_PORT};DATABASE=master;trusted_connection=yes;"  # Windows Authentication Local Testing Use
        else:
            return f"mssql+aioodbc:///?odbc_connect=DRIVER={self.MSSQL_DRIVER};SERVER={self.MSSQL_HOST},{self.MSSQL_PORT};DATABASE=master;UID={self.MSSQL_USER};PWD={self.MSSQL_PASSWORD};"

    def is_production(self) -> bool:
        return self.ENV.lower() in ["prod", "production"]


try:
    CONFIG = Settings()
except ValidationError as e:
    print("Settings validation failed:")
    for error in e.errors():
        print(f"Variable - {error['loc']}: {error['msg']}, please check your .env file")
except Exception as e:
    print(f"Unexpected error in Settings(): {str(e)}")
    raise e
