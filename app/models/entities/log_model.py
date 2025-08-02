from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from sqlalchemy import Enum as SAEnum, DateTime

from app.utils.enum import LogLevel


class Log(SQLModel, table=True):
    __tablename__ = "log"

    id: int = Field(primary_key=True)
    level: str = Field(sa_column=SAEnum(LogLevel), default=LogLevel.I)
    module: str = Field(default=None)
    message: str = Field(default=None)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        nullable=False
    )
