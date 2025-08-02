from app.core.decorators import async_log_and_raise_error, decorateAllFunctionInClass
from app.utils.logger import Logger
from sqlalchemy.ext.asyncio import AsyncSession


@decorateAllFunctionInClass(async_log_and_raise_error())
class BaseController:
    """
    Base controller class that provides common functionality for all controllers.
    It can be extended by other controllers to inherit common methods and properties.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.log = Logger("db_controller_log")  # Placeholder for log manager, can be initialized in subclasses
