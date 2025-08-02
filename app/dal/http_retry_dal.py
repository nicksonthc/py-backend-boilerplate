import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List

from dateutil.relativedelta import relativedelta
from sqlalchemy import ChunkedIteratorResult, Date, cast, delete, select, update

from app.core.circuit_breaker import CircuitBreaker
from app.db.session import get_session_context
from app.models.entities.http_retry_model import HttpRetry
from app.models.schemas.http_retry_schema import HttpRetryCreate
from app.utils.enum import HttpRetryStatus


class HttpRetryDAL:

    CLEAN_UP_PER_BATCH = 1000

    @staticmethod
    @CircuitBreaker.circuit_breaker_context
    @asynccontextmanager
    async def create_http_retry(http_retry: HttpRetryCreate):
        async with get_session_context() as session:
            db_obj = HttpRetry(**http_retry.model_dump(mode="json"))
            session.add(db_obj)
            await session.flush()
            await session.refresh(db_obj)
            yield db_obj

    @staticmethod
    @CircuitBreaker.circuit_breaker_context
    @asynccontextmanager
    async def read_http_retry(id: int):
        async with get_session_context() as session:
            result: ChunkedIteratorResult = await session.execute(select(HttpRetry).where(HttpRetry.id == id))
            db_obj: HttpRetry = result.scalar_one_or_none()
            yield db_obj

    @staticmethod
    @CircuitBreaker.circuit_breaker
    async def incr_http_retry_attempts(id: int):
        async with get_session_context() as session:
            result: ChunkedIteratorResult = await session.execute(
                update(HttpRetry)
                .where(HttpRetry.id == id)
                .values(attempts=HttpRetry.attempts + 1)
                .returning(HttpRetry.attempts)
            )
            return result.scalar_one_or_none()

    @staticmethod
    @CircuitBreaker.circuit_breaker
    async def complete_http_retry(id: int, response: dict):
        async with get_session_context() as session:
            await session.execute(
                update(HttpRetry)
                .where(HttpRetry.id == id)
                .values(
                    status=HttpRetryStatus.COMPLETED.value,
                    response=response,
                    completed_at=datetime.now(timezone.utc),
                )
            )

    @staticmethod
    @CircuitBreaker.circuit_breaker
    async def delete_http_retry(id: int):
        async with get_session_context() as session:
            await session.execute(
                update(HttpRetry)
                .where(HttpRetry.id == id)
                .values(
                    status=HttpRetryStatus.DELETED.value,
                    completed_at=datetime.now(timezone.utc),
                )
            )

    @staticmethod
    @CircuitBreaker.circuit_breaker_context
    @asynccontextmanager
    async def get_incompleted_http_retry():
        async with get_session_context() as session:
            result: ChunkedIteratorResult = await session.execute(
                select(HttpRetry).where(HttpRetry.status == HttpRetryStatus.PROCESSING.value).order_by(HttpRetry.id)
            )
            db_objs: List[HttpRetry] = result.scalars().all()
            yield db_objs

    @classmethod
    @CircuitBreaker.circuit_breaker
    async def clean_http_retry(cls, remove_period: relativedelta):
        async with get_session_context() as session:
            cutoff = (datetime.now(timezone.utc) - remove_period).date()
            while True:
                result = await session.execute(
                    select(HttpRetry.id)
                    .where(
                        cast(HttpRetry.created_at, Date) <= cutoff,
                        HttpRetry.status != HttpRetryStatus.PROCESSING.value,
                    )
                    .limit(cls.CLEAN_UP_PER_BATCH)
                )
                ids = result.all()
                if not ids:
                    break
                await session.execute(delete(HttpRetry).where(HttpRetry.id.in_(ids)))
                await asyncio.sleep(0.1)
