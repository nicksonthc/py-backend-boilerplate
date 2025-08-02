from typing import TYPE_CHECKING, List
from pydantic import BaseModel, Field, model_validator
from app.core.response import APIResponse
from app.utils.conversion import get_local_dt_iso
from app.utils.enum import *
from datetime import datetime

if TYPE_CHECKING:
    from app.models.entities.log_event_model import LogEvent


class LogEventCreate(BaseModel):
    station_name: str
    module: Module  # Changed from str to Module enum
    station_code: int
    message_content: str
    event_at: datetime | None = None
    task_id: int | None = None
    item_id: int | None = None
    event: EventType = EventType.TCPIP
    direction: EventDirection = EventDirection.SEND
    source_system: str = str()
    source_ip: str = str()
    destination_system: str = str()
    destination_ip: str = str()
    protocol: EventProtocol = EventProtocol.TCPIP
    message_size: int | None = None

    @model_validator(mode="before")
    @classmethod
    def set_message_size(cls, data: dict):
        if "message_content" in data:
            data["message_size"] = len(data["message_content"])
        return data

    @model_validator(mode="before")
    @classmethod
    def set_event_at(cls, data: dict):
        if data.get("event_at") is None:
            data["event_at"] = datetime.now()
        return data


class LogEventOut(LogEventCreate):
    message: str
    created_at: str | None = None
    event_at: str | None = None
    message_size: int | None = None

    @classmethod
    def from_sqlmodel(cls, sqlmodel_obj: "LogEvent"):

        return cls(
            station_name=sqlmodel_obj.station_name,
            module=sqlmodel_obj.module,
            station_code=sqlmodel_obj.station_code,
            task_id=sqlmodel_obj.task_id,
            item_id=sqlmodel_obj.item_id,
            message=sqlmodel_obj.message_content,
            event=sqlmodel_obj.event,
            event_at=str(get_local_dt_iso(sqlmodel_obj.event_at)) if sqlmodel_obj.event_at else None,
            created_at=str(get_local_dt_iso(sqlmodel_obj.created_at)) if sqlmodel_obj.created_at else None,
            direction=sqlmodel_obj.direction,
            source_system=sqlmodel_obj.source_system,
            source_ip=sqlmodel_obj.source_ip,
            destination_system=sqlmodel_obj.destination_system,
            destination_ip=sqlmodel_obj.destination_ip,
            protocol=sqlmodel_obj.protocol,
            message_size=sqlmodel_obj.message_size,
            message_content=sqlmodel_obj.message_content,
        )


class LogEventOutResponse(APIResponse):
    data: List[LogEventOut] = Field(default=[])
