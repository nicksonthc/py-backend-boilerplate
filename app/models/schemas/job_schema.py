from datetime import datetime
from typing import Any, List
from pydantic import BaseModel, Field

from app.core.response import APIResponse
from app.utils.conversion import get_local_dt_iso
from app.utils.enum import JobType, JobStatus


class JobBase(BaseModel):
    id: int | None = None
    type: JobType = Field(description="Job type")
    status: JobStatus = Field(default=JobStatus.AVAILABLE, description="Job status")
    priority: int = Field(default=1, ge=1, le=5, description="Job priority (1-5)")
    assigned_to: str | None = Field(default=None, max_length=100, description="Person assigned to job")
    order_id: int | None = Field(default=None, description="Associated order ID")


class JobOut(JobBase):
    created_at: str
    updated_at: str | None = None
    completed_at: str | None = None

    class Config:
        from_attributes = True

    @classmethod
    async def from_sqlmodel(cls, sqlmodel_obj: "Job"):
        return cls(
            id=sqlmodel_obj.id,
            status=sqlmodel_obj.status,
            type=sqlmodel_obj.type,
            priority=sqlmodel_obj.priority,
            assigned_to=sqlmodel_obj.assigned_to,
            order_id=sqlmodel_obj.order_id,
            created_at=get_local_dt_iso(sqlmodel_obj.created_at),
            updated_at=get_local_dt_iso(sqlmodel_obj.updated_at),
            completed_at=get_local_dt_iso(sqlmodel_obj.completed_at),
        )


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    type: JobType | None = Field(default=None, description="Job type")
    status: JobStatus | None = Field(default=None, description="Job status")
    priority: int | None = Field(default=None, ge=1, le=5, description="Job priority (1-5)")
    assigned_to: str | None = Field(default=None, max_length=100, description="Person assigned to job")
    order_id: int | None = Field(default=None, description="Associated order ID")


class JobInDBBase(JobBase):
    id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class Job(JobInDBBase):
    pass


class JobInDB(JobInDBBase):
    pass


# Schema for responses with orders
class JobWithOrders(JobInDBBase):
    orders: list[dict[str, Any]] = []


class JobOutResponse(APIResponse):
    data: List[JobOut] = Field(default=[])
