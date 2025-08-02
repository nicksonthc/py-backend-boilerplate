from datetime import datetime
from typing import Any, List
from pydantic import BaseModel, Field

from app.core.response import APIResponse
from app.utils.conversion import get_local_dt_iso
from app.utils.enum import OrderType, OrderStatus


class OrderBase(BaseModel):
    id: int | None = None
    type: OrderType = Field(description="Order type")
    status: OrderStatus = Field(default=OrderStatus.AVAILABLE, description="Order status")
    job_id: list[int] = Field(default=None, description="Associated job ID")


class OrderCreate(BaseModel):
    type: OrderType = Field(description="Order type")


class OrderUpdate(BaseModel):
    type: OrderType | None = Field(default=None, description="Order type")
    status: OrderStatus | None = Field(default=None, description="Order status")
    job_id: int | None = Field(default=None, description="Associated job ID")


class OrderInDBBase(OrderBase):
    id: int | None = None

    class Config:
        from_attributes = True


class OrderOut(OrderBase):
    id: int | None = None
    jobs: list[dict[str, Any]] | None = None
    created_at: str
    updated_at: str | None = None
    completed_at: str | None = None

    class Config:
        from_attributes = True

    @classmethod
    async def from_sqlmodel(cls, sqlmodel_obj: "Order"):
        job_ids = [job.id for job in sqlmodel_obj.jobs]
        return cls(
            id=sqlmodel_obj.id,
            status=sqlmodel_obj.status,
            type=sqlmodel_obj.type,
            job_id=job_ids,
            created_at=get_local_dt_iso(sqlmodel_obj.created_at),
            updated_at=get_local_dt_iso(sqlmodel_obj.updated_at),
            completed_at=get_local_dt_iso(sqlmodel_obj.completed_at),
        )


class OrderOutResponse(APIResponse):
    data: List[OrderOut] = Field(default=[])


# Schema for responses with job details
class OrderWithJob(OrderBase):
    job: dict[str, Any] | None = None
