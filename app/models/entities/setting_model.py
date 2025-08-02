from typing import Dict, Optional
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import DateTime, func


class Setting(SQLModel, table=True):
    """Model representing a system setting"""

    __tablename__ = "settings"

    id: int = Field(primary_key=True)
    name: str = Field(nullable=False)
    value: Dict = Field(sa_column=Column(JSON, nullable=False))
    description: Optional[str] = Field(nullable=True)
    created_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    updated_at: datetime | None = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )

    def __repr__(self):
        return f"<Setting {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
