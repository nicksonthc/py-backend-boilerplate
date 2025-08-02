from sqlalchemy import DateTime, Enum as SAEnum
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

from app.utils.enum import EventDirection, EventProtocol, EventType, Module


class LogEvent(SQLModel, table=True):
    __tablename__ = "log_event"
    id: int | None = Field(primary_key=True)
    station_name: str = Field(nullable=True)  # Conveyor / Ingress 1 / Egress 1
    module: str = Field(sa_column=SAEnum(Module))  # module AS,CZ,INGRESS,EGRESS,WMS,
    station_code: int = Field(nullable=False)  # query by station perspective e.g ingress/egress/asrs/conveyor
    task_id: int = Field(nullable=True)  # query by task perspective
    item_id: int = Field(nullable=True)  # query by item id perspective
    event: EventType = Field(nullable=False, max_length=20)
    direction: EventDirection = Field(nullable=False)  # Direction of the message: SEND or RECEIVE.

    source_system: str = Field(nullable=True)  # PLC,WMS
    source_ip: str = Field(nullable=True)  # IP address + port of the sender.
    destination_system: str = Field(nullable=True)  # PLC,WMS
    destination_ip: str = Field(nullable=True)  # IP address +port of the sender.
    protocol: EventProtocol = Field(nullable=True)  # TCP, UDP, HTTP .
    message_size: int = Field(nullable=True)
    message_content: str = Field(nullable=False)

    event_at: datetime = Field(
        default=None, sa_type=DateTime(timezone=True), nullable=False
    )  # The datetime tcp event take place
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), sa_type=DateTime(timezone=True), nullable=False
    )
