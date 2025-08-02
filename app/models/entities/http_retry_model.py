from http import HTTPMethod
from typing import List

from sqlmodel import JSON, CheckConstraint, Column, Field, SQLModel

from app.models.entities.base_timestamp import BaseTimestamp
from app.utils.enum import HttpRetryStatus


class HttpRetryBase(SQLModel):
    id: int = Field(primary_key=True)
    status: str = Field(default=HttpRetryStatus.PROCESSING, nullable=False)
    method: str = Field(nullable=False)
    url: str = Field(nullable=False)
    timeout: int = Field(nullable=False)
    payload: dict = Field(default={}, sa_column=Column(JSON))
    headers: dict = Field(default={}, sa_column=Column(JSON))
    reference: dict = Field(default={}, sa_column=Column(JSON))
    response: dict = Field(default={}, sa_column=Column(JSON))
    attempts: int = Field(default=0, nullable=False)
    retry_limit: int = Field(nullable=False)
    retry_interval: int = Field(nullable=False)
    pred_ids: List[int] = Field(default=[], sa_column=Column(JSON))


class HttpRetry(BaseTimestamp, HttpRetryBase, table=True):
    __tablename__ = "http_retry"
    __table_args__ = (
        CheckConstraint(
            sqltext=f"status IN ({", ".join(repr(e.value) for e in HttpRetryStatus)})",
            name="check_http_retry_status",
        ),
        CheckConstraint(
            sqltext=f"method IN ({", ".join(repr(e.value) for e in HTTPMethod)})",
            name="check_http_retry_method",
        ),
    )
