from datetime import datetime
from http import HTTPMethod
from typing import List

from pydantic import BaseModel, Field, HttpUrl

from app.core.response import APIResponse
from app.utils.enum import HttpRetryStatus


class HttpRetryBase(BaseModel):
    method: HTTPMethod
    url: HttpUrl
    timeout: int
    payload: dict
    headers: dict
    reference: dict
    retry_limit: int
    retry_interval: int


class HttpRetryCreate(HttpRetryBase):
    pred_ids: List[int] = Field(default_factory=list)


class HttpRetryIn(HttpRetryBase):
    pass


class HttpRetryOut(HttpRetryBase):
    id: int
    attempts: int
    created_at: datetime
    completed_at: datetime | None
    status: HttpRetryStatus
    response: dict | None
    pred_ids: List[int]


class HttpRetryOutResponse(APIResponse):
    data: List[HttpRetryOut] = Field(default=[])
