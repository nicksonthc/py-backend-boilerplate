import asyncio

from typing import List
from sqlalchemy import func
from datetime import datetime
from sqlmodel import select, update, delete, cast, Date
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas.log_event_schema import LogEventCreate
from app.utils.enum import *
from app.models.entities.log_event_model import LogEvent
from app.core.decorators import decorateAllFunctionInClass
from app.core.circuit_breaker import CircuitBreaker


@decorateAllFunctionInClass(CircuitBreaker.circuit_breaker)
class LogEventDAL:
    CHUNK_SIZE = 1000

    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        log_event: LogEventCreate,
    ):

        log = LogEvent(**log_event.model_dump())
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)

    async def batch_log_events(self, log_events: List[LogEvent]):
        """Batch insert multiple log events in a single transaction"""
        if not log_events:
            return

        try:
            self.session.add_all(log_events)
        except Exception as e:
            print(f"Failed to batch log events: {e}")
            await self.session.rollback()

    async def get_logs(
        self,
        station_name: str,
        module: Module,
        event: EventType,
        from_date: datetime,
        to_date: datetime,
        page: int,
        per_page: int,
    ) -> tuple[List[LogEvent], int]:

        conditions = []

        if station_name:
            conditions.append(LogEvent.station_name == station_name)
        if module:
            conditions.append(LogEvent.module == module)
        if event:
            conditions.append(LogEvent.event == event)
        if from_date:
            conditions.append(LogEvent.event_at >= from_date)
        if to_date:
            conditions.append(LogEvent.event_at <= to_date)

        count_query = select(func.count()).select_from(LogEvent).where(*conditions)
        result = await self.session.execute(count_query)
        total = result.scalar_one()

        query = select(LogEvent).where(*conditions).order_by(LogEvent.event_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await self.session.execute(query)
        data = result.scalars().all()
        return data, total

    async def get_logs_by_content(
        self,
        filter_str: str,
        station_name: str | None = None,
        module: Module | None = None,
        event: EventType | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[List[LogEvent], int]:

        # Build base query conditions
        conditions = []

        # Add filter for message content
        conditions.append(LogEvent.message_content.contains(filter_str))

        # Add optional filters if provided
        if station_name:
            conditions.append(LogEvent.station_name == station_name)
        if module:
            conditions.append(LogEvent.module == module)
        if event:
            conditions.append(LogEvent.event == event)
        if from_date:
            conditions.append(LogEvent.event_at >= from_date)
        if to_date:
            conditions.append(LogEvent.event_at <= to_date)

        count_query = select(func.count()).select_from(LogEvent).where(*conditions)
        result = await self.session.execute(count_query)
        total = result.scalar_one()

        query = select(LogEvent).where(*conditions).order_by(LogEvent.event_at.desc())

        query = query.offset((page - 1) * per_page).limit(per_page)

        result = await self.session.execute(query)
        return result.all(), total

    async def clean_up_log_event(self, remove_period: relativedelta):

        cutoff_date = (datetime.now() - remove_period).date()
        while True:
            # Select up to chunk_size ids to delete
            result = await self.session.execute(
                select(LogEvent.id).where(cast(LogEvent.created_at, Date) <= cutoff_date).limit(LogEventDAL.CHUNK_SIZE)
            )
            ids = result.all()
            if not ids:
                break
            # Delete this chunk
            await self.session.execute(delete(LogEvent).where(LogEvent.id.in_(ids)))
            await self.session.commit()
            await asyncio.sleep(0.1)  # to release context for other coroutine
