from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Enum
from app.utils.enum import JobType, JobStatus
from app.models.entities.base_timestamp import BaseTimestamp

if TYPE_CHECKING:
    from app.models.entities.order_model import Order


class JobBase(SQLModel):
    id: int = Field(primary_key=True)

    type: str = Field(sa_column=Enum(JobType), default=JobType.DEPOSIT)
    status: str = Field(sa_column=Enum(JobStatus), default=JobStatus.AVAILABLE)

    priority: int = Field(default=1, ge=1, le=5)
    assigned_to: str | None = Field(default=None, max_length=100)

    # Foreign key to Order (parent)
    order_id: int = Field(foreign_key="orders.id")

    class Config:
        from_attributes = True


class Job(BaseTimestamp, JobBase, table=True):
    __tablename__ = "jobs"

    # Relationship - a job belongs to one order
    order: "Order" = Relationship(back_populates="jobs")

    class Config:
        from_attributes = True
