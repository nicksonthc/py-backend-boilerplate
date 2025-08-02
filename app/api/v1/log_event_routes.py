from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.log_event_controller import LogEventController
from app.core.decorators import async_log_and_return_error
from app.models.schemas.job_schema import JobCreate, JobUpdate, Job, JobOutResponse
from app.db.session import get_session
from app.models.schemas.log_event_schema import LogEventCreate, LogEventOut, LogEventOutResponse
from app.utils.conversion import get_date_now_iso, get_utc_dt
from app.utils.enum import EventType, JobStatus, JobType, Module
from app.utils.logger import recv_http_logger
from app.core.response import Pagination, Response

router = APIRouter(prefix="/log-events", tags=["log events"])


# Dependency to get controller
async def get_log_event_controller(session: AsyncSession = Depends(get_session)) -> LogEventController:
    return LogEventController(session)


@router.post("/", status_code=status.HTTP_200_OK)
@async_log_and_return_error(recv_http_logger)
async def create_log_event(
    log_event: LogEventCreate, controller: LogEventController = Depends(get_log_event_controller)
):
    """Create a new log event"""
    await controller.create_log_event(log_event)
    return Response()


@router.get("", description="Get the log of the system", response_model=LogEventOutResponse)
@async_log_and_return_error(recv_http_logger)
async def get_log(
    station_name: Annotated[str, Query(description="The station name")],
    module: Annotated[Module, Query(description="The module to query")] | None = None,
    event: Annotated[EventType, Query(description="The event type to query")] | None = None,
    from_date: Annotated[
        str, Query(description="From datetime, YYYY-MM-DD", examples=["2024-11-20T00:00:00"])
    ] = get_date_now_iso()[0],
    to_date: Annotated[
        str, Query(description="To datetime YYYY-MM-DD", examples=["2024-11-22T12:00:00"])
    ] = get_date_now_iso()[1],
    page: Annotated[int, Query(description="The page number", ge=1)] = 1,
    per_page: Annotated[int, Query(description="The number of logs per page", ge=1)] = 100,
    search_string: Annotated[str | None, Query(description="Search string to filter message content")] = None,
    controller: LogEventController = Depends(get_log_event_controller),
):
    start = get_utc_dt(datetime.fromisoformat(from_date))
    end = get_utc_dt(datetime.fromisoformat(to_date))

    if search_string:
        logs, total_length = await controller.get_logs_by_content(
            filter_str=search_string,
            station_name=station_name,
            module=module,
            event=event,
            from_date=start,
            to_date=end,
            page=page,
            per_page=per_page,
        )
    else:
        logs, total_length = await controller.get_logs(station_name, module, event, start, end, page, per_page)

    logs_pydantic = [LogEventOut.from_sqlmodel(log) for log in logs]
    pagination = Pagination(
        page=page,
        per_page=per_page,
        total_items=total_length,
    )
    return Response(api_response_model=LogEventOutResponse(data=logs_pydantic, pagination=pagination))
