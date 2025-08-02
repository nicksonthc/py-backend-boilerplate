from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, DateTime


class BaseTimestamp(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), sa_type=DateTime(timezone=True), nullable=False
    )

    updated_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True), nullable=True)
    completed_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True), nullable=True)
