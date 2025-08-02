import asyncio

from typing import List

from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy import delete, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil.relativedelta import relativedelta

from .base_dal import BaseDAL
from app.models.entities.log_model import Log
from app.core.circuit_breaker import CircuitBreaker
from app.core.decorators import decorateAllFunctionInClass


@decorateAllFunctionInClass(CircuitBreaker.circuit_breaker)
class LogDAL(BaseDAL):

    CHUNK_SIZE = 1000  # Define the chunk size for batch processing

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def batch_log(self, logs: List[Log]):
        """Batch insert multiple log entries in a single transaction"""
        self.session.add_all(logs)

    async def clean_up_log(self, remove_period: relativedelta):
        """Clean up log entries older than the specified period"""
        cutoff_date = (datetime.now() - remove_period).date()
        while True:
            # Select up to chunk_size ids to delete
            result = await self.session.execute(
                select(Log.id).where(cast(Log.created_at, Date) <= cutoff_date).limit(LogDAL.CHUNK_SIZE)
            )
            ids = result.all()
            if not ids:
                break
            # Delete this chunk
            await self.session.execute(delete(Log).where(Log.id.in_(ids)))
            await asyncio.sleep(0.1)  # to release context for other coroutine
