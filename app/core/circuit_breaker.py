import asyncio
import functools
from contextlib import asynccontextmanager
from datetime import datetime

from sqlalchemy.exc import OperationalError

# A circuit breaker that use to track when db down and stop the other services
# Currently implement in http_retry_manager, http incoming request in middleware, and tcp_server
# TODO add to other service handler or logic handler in future class to make sure no other db access after db is down


class CircuitBreaker:

    db_is_down: bool = False
    db_down_start_time: str = ""
    db_down_reason: str = ""
    suggest_retry_interval = 5  # seconds

    @classmethod
    def is_db_down(cls):
        return cls.db_is_down

    @classmethod
    def start(cls, e: Exception):
        if cls.db_is_down == True:
            return
        cls.db_is_down = True
        cls.db_down_start_time = datetime.now().isoformat()
        cls.db_down_reason = str(e)

    @classmethod
    def stop(cls):
        cls.db_is_down = False
        cls.db_down_start_time = ""
        cls.db_down_duration = ""
        cls.db_down_reason = ""

    @classmethod
    @asynccontextmanager
    async def handle_exception(cls, func_name: str, args, kwargs):
        try:
            yield
        except OperationalError as e:
            # Extract function name and error details
            error_msg = f"{func_name} exception: {e}"
            cls.start(error_msg)
            print(f"Retrying {func_name} due to {e.args}.")
            await asyncio.sleep(cls.suggest_retry_interval)
            if args[0] and hasattr(args[0], "session"):
                await args[0].session.rollback()
        except Exception as e:
            # Extract function name and error details
            error_msg = f"{func_name} exception: {e}"
            raise Exception(error_msg)

    @classmethod
    def circuit_breaker(cls, original_function):
        """
        Circuit breaker decorator that use on retry code area
        Will catch Operational Error which is normally deal with DB disconnect or DB unable to connect error, and start circuit breaker

        For dal layer that inject session inside class, can implement at dal layer (Ex: setting_dal)
        For dal layer that use get_session_context, can implement at controller layer (Ex: http_retry_dal, http_retry_controller)
        """

        @functools.wraps(original_function)
        async def decorated_function(*args, **kwargs):
            while True:
                async with cls.handle_exception(original_function.__qualname__, args, kwargs):
                    res = await original_function(*args, **kwargs)
                    cls.stop()
                    return res

        return decorated_function

    @classmethod
    def circuit_breaker_context(cls, original_function):
        @asynccontextmanager
        @functools.wraps(original_function)
        async def decorated_function(*args, **kwargs):
            while True:
                async with cls.handle_exception(original_function.__qualname__, args, kwargs):
                    async with original_function(*args, **kwargs) as res:
                        yield res
                        cls.stop()
                        return

        return decorated_function
