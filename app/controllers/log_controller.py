from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil.relativedelta import relativedelta

from app.dal.log_dal import LogDAL, Log
from .base_controller import BaseController
from app.core.decorators import async_log_and_raise_error, decorateAllFunctionInClass


@decorateAllFunctionInClass(async_log_and_raise_error())
class LogController(BaseController):

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.dal = LogDAL(session)

    async def batch_log(self, logs: List[Log]):
        """Batch insert multiple log entries in a single transaction"""
        if not logs:
            return
        await self.dal.batch_log(logs)

    async def clean_up_log(self, remove_period: relativedelta):
        await self.dal.clean_up_log(remove_period)
