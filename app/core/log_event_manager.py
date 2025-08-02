import asyncio
from typing import List
from datetime import datetime
from app.models.schemas.log_event_schema import LogEventCreate
from app.utils.enum import *


class LogEventManager:
    # Class-level batch configuration
    event_queue = asyncio.Queue()
    batch_size = 20
    flush_interval = 5.0  # seconds
    _batch_task = None
    _shutdown = False
    event_loop = None

    @classmethod
    def initialize(cls, event_loop: asyncio.AbstractEventLoop):
        cls.event_loop = event_loop
        # Start the batch processing task
        if cls._batch_task is None:
            cls._batch_task = event_loop.create_task(cls._batch_processor())

    @classmethod
    async def shutdown(cls):
        """Gracefully shutdown the event log manager and flush remaining logs"""
        cls._shutdown = True
        if cls._batch_task:
            await cls._batch_task

    @classmethod
    async def _batch_processor(cls):
        """Background task that processes event log entries in batches"""
        batch = []
        last_flush = datetime.now()

        while not cls._shutdown:
            try:
                # Try to get an event log entry with timeout
                try:
                    event_entry = await asyncio.wait_for(cls.event_queue.get(), timeout=0.1)
                    batch.append(event_entry)
                except asyncio.TimeoutError:
                    pass

                current_time = datetime.now()
                time_since_flush = (current_time - last_flush).total_seconds()

                # Flush if batch is full or flush interval has passed
                should_flush = len(batch) >= cls.batch_size or (batch and time_since_flush >= cls.flush_interval)

                if should_flush:
                    await cls._flush_batch(batch)
                    batch.clear()
                    last_flush = current_time

            except Exception as e:
                print(f"Error in event batch processor: {e}")
                await asyncio.sleep(1)

        # Flush remaining logs on shutdown
        if batch:
            await cls._flush_batch(batch)

    @classmethod
    async def _flush_batch(cls, batch: List[LogEventCreate]):
        """Flush a batch of event log entries to the database"""
        if not batch:
            return

        try:
            from app.controllers.log_event_controller import LogEventController
            from app.models.entities.log_event_model import LogEvent
            from app.db.session import get_session_context

            async with get_session_context() as session:
                log_event_controller = LogEventController(session)
                log_events: List[LogEvent] = []
                for entry in batch:
                    log_events.append(LogEvent(**entry.model_dump()))

                await log_event_controller.add_log_event_batch(log_events)
        except Exception as e:
            print(f"Failed to flush event log batch: {e}")

    @classmethod
    def _add_to_queue(cls, event_entry: LogEventCreate):
        """Add event log entry to the batch queue"""
        try:
            cls.event_queue.put_nowait(event_entry)
        except asyncio.QueueFull:
            print(f"Event log queue is full, dropping event: {event_entry.message_content}")
