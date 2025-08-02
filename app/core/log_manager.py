import asyncio

from typing import List
from colorama import Fore, Style
from dataclasses import dataclass
from app.utils.enum import LogLevel
from app.utils.scheduler import scheduler
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler


@dataclass
class LogEntry:
    level: str
    module: str
    message: str
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)


class LogManager:
    # Class-level batch configuration
    log_queue = asyncio.Queue()
    batch_size = 20
    flush_interval = 5.0  # seconds
    _batch_task = None
    _shutdown = False
    event_loop = None

    @classmethod
    def initialize(cls, event_loop: asyncio.AbstractEventLoop):
        from app.utils.logger import Logger

        cls.console_log = Logger("LogMananger")
        cls.event_loop = event_loop
        # Start the batch processing task
        if cls._batch_task is None:
            cls._batch_task = event_loop.create_task(cls._batch_processor())

    @classmethod
    async def shutdown(cls):
        """Gracefully shutdown the log manager and flush remaining logs"""
        cls._shutdown = True
        if cls._batch_task:
            await cls._batch_task

    @classmethod
    async def _batch_processor(cls):
        """Background task that processes log entries in batches"""
        batch = []
        last_flush = datetime.now()

        while not cls._shutdown:
            try:
                # Try to get a log entry with timeout
                try:
                    log_entry = await asyncio.wait_for(cls.log_queue.get(), timeout=0.1)
                    batch.append(log_entry)
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
                cls.console_log.error_to_console_only(f"Error in batch processor: {e}")
                await asyncio.sleep(1)

        # Flush remaining logs on shutdown
        if batch:
            await cls._flush_batch(batch)

    @classmethod
    async def _flush_batch(cls, batch: List[LogEntry]):
        """Flush a batch of log entries to the database"""
        if not batch:
            return

        from app.models.entities.log_model import Log
        from app.db.session import get_session_context
        from app.controllers.log_controller import LogController

        try:
            async with get_session_context() as session:
                log_controller = LogController(session)
                logs = []
                for entry in batch:
                    log = Log(
                        level=entry.level, module=entry.module, message=entry.message
                    )
                    logs.append(log)
                await log_controller.batch_log(logs)
        except Exception as e:
            cls.console_log.error_to_console_only(f"Failed to flush log batch: {e}")

    def __init__(self, name):
        self.name = name

    def info(self, log: str):
        """Add info log to batch queue"""
        self._add_to_queue(LogLevel.I, log)

    def warning(self, log: str):
        """Add warning log to batch queue"""
        self._add_to_queue(LogLevel.W, log)

    def error(self, log: str):
        """Add error log to batch queue"""
        self._add_to_queue(LogLevel.E, log)

    def _add_to_queue(self, level: str, message: str):
        """Add log entry to the batch queue"""
        from app.utils.conversion import datetime_console

        log_entry = LogEntry(level=level, module=self.name, message=message)

        try:
            self.log_queue.put_nowait(log_entry)
        except asyncio.QueueFull:
            self.console_log.error_to_console_only(f"Log queue is full, dropping log: {message}")


class LogCleanUpService:
    DATA_THRESHOLD = relativedelta(months=6)

    @classmethod
    async def initialize(cls):
        await cls.register_schedule_task(scheduler)

    @classmethod
    async def register_schedule_task(cls, scheduler: AsyncIOScheduler):
        scheduler.add_job(cls.clean_up_log, "cron", day=1, hour=0, minute=0, args=[cls.DATA_THRESHOLD])
        # scheduler.add_job(cls.clean_up_log, "interval", seconds=10, args=[cls.DATA_THRESHOLD])

    @classmethod
    async def clean_up_log(cls, remove_period: relativedelta):
        from app.db.session import get_session_context
        from app.controllers.log_controller import LogController

        try:
            async with get_session_context() as session:
                log_controller = LogController(session)
                await log_controller.clean_up_log(remove_period)
        except Exception as e:
            LogManager.console_log.error_to_console_only(f"Failed to clean up logs: {e}")
