from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, Enum
from app.utils.enum import OrderType, OrderStatus
from app.models.entities.base_timestamp import BaseTimestamp

if TYPE_CHECKING:
    from app.models.entities.job_model import Job


class OrderBase(SQLModel):
    id: int | None = Field(primary_key=True)
    type: str = Field(sa_column=Enum(OrderType), default=OrderType.DEPOSIT)
    status: str = Field(sa_column=Enum(OrderStatus), default=OrderStatus.AVAILABLE)


class Order(BaseTimestamp, OrderBase, table=True):
    __tablename__ = "orders"

    # Relationship - an order has multiple jobs
    jobs: list["Job"] = Relationship(back_populates="order", sa_relationship_kwargs={"lazy": "selectin"})
