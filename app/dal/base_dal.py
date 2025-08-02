from sqlalchemy.ext.asyncio import AsyncSession
from app.core.decorators import async_log_and_raise_error, decorateAllFunctionInClass
from app.utils.logger import Logger


@decorateAllFunctionInClass(async_log_and_raise_error())
class BaseDAL:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.log = Logger("db_dal_log")
