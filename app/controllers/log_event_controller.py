from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.dal.log_event_dal import LogEventDAL, LogEvent
from app.models.schemas.log_event_schema import LogEventCreate
from app.utils.enum import EventType, EventDirection, EventProtocol, Module


class LogEventController:
    def __init__(self, session: AsyncSession):
        self.dal = LogEventDAL(session)
        self.session = session

    async def create_log_event(self, log_event: LogEventCreate):
        """Create a new log event"""
        await self.dal.log(log_event)

    async def add_log_event_batch(self, log_events: List[LogEvent]):
        await self.dal.batch_log_events(log_events)

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
    ):
        return await self.dal.get_logs_by_content(
            filter_str, station_name, module, event, from_date, to_date, page, per_page
        )

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
        return await self.dal.get_logs(station_name, module, event, from_date, to_date, page, per_page)
