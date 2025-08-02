from __future__ import annotations
from http import HTTPStatus
import types, functools
from typing import TYPE_CHECKING

from .response import Response


if TYPE_CHECKING:
    from app.utils.logger import Logger


class BadRequestException(Exception):
    def __init__(self, original_exception):
        super().__init__(f"WMSValidation: {original_exception}")
        self.original_exception = original_exception


def async_log_and_return_error(log_func: Logger):
    def argument_decorator(original_function):
        @functools.wraps(original_function)
        async def decorated_function(*args, **kwargs):
            try:
                return await original_function(*args, **kwargs)

            except BadRequestException as e:
                detail_error = (
                    f"{original_function.__qualname__}() with positional "
                    f"argument(s) {args}, and keyword argument(s) {kwargs}, raise Exception:{repr(e)}"
                )
                log_func.error(detail_error)
                return Response(
                    status=False, code=HTTPStatus.BAD_REQUEST, message=repr(e.original_exception), error=None
                )
            except Exception as e:
                detail_error = (
                    f"{original_function.__qualname__}() with positional "
                    f"argument(s) {args}, and keyword argument(s) {kwargs}, raise Exception:{repr(e)}"
                )
                log_func.error(detail_error)
                return Response(
                    status=False, code=HTTPStatus.INTERNAL_SERVER_ERROR, message=repr(e), error=detail_error
                )

        return decorated_function

    return argument_decorator


def async_log_and_suppress_error(log_func: Logger):
    def argument_decorator(original_function):
        @functools.wraps(original_function)
        async def decorated_function(*args, **kwargs):
            try:
                return await original_function(*args, **kwargs)
            except Exception as e:
                log_func.error(f"{original_function.__qualname__}() raise Exception: {e}")

        return decorated_function

    return argument_decorator


def log_and_suppress_error(log_func: Logger):
    def argument_decorator(original_function):
        @functools.wraps(original_function)
        def decorated_function(*args, **kwargs):
            try:
                return original_function(*args, **kwargs)
            except Exception as e:
                log_func.error(f"{original_function.__qualname__}() raised Exception: {e}")

        return decorated_function

    return argument_decorator


def async_log_and_raise_error():
    """
    Decorator for async functions that logs and raises errors.
    Mainly use by controller layer and dal layer so able to raise exception to upper layer and perform db session rollback on every related operation
    Will catch Operational Error which is normally deal with DB disconnect or DB unable to connect error, and start circuit breaker
    """

    def argument_decorator(original_function):
        @functools.wraps(original_function)
        async def decorated_function(*args, **kwargs):
            try:
                return await original_function(*args, **kwargs)
            except Exception as e:
                # Extract function name and error details
                func_name = original_function.__qualname__
                error_msg = f"{func_name} exception: {e}"
                raise Exception(error_msg)

        return decorated_function

    return argument_decorator


def decorateAllFunctionInClass(decorator):
    """
    Decorate all functions with the argument decorator by checking the reflection of iterable obj whether it is equal to types.FunctionType.

    Example Usage:

    @decorateAllFunctionInClass(log_and_suppress_error())
    class YourClass:
        def __init__(self):
            pass

        def functionOne(self):
            print("Function One")

        async def functionTwo(self):
            print("Function Two")

    """

    def decorate(_class):
        for k, v in _class.__dict__.items():
            # Skip methods like __init__, __new__, etc.
            if k.startswith("__") and k.endswith("__"):
                continue

            if isinstance(v, types.FunctionType):  # Regular function
                setattr(_class, k, decorator(v))

            elif isinstance(v, classmethod):  # Class method
                func = v.__func__
                setattr(_class, k, classmethod(decorator(func)))

            elif isinstance(v, staticmethod):  # Static method
                func = v.__func__
                setattr(_class, k, staticmethod(decorator(func)))

            elif isinstance(v, types.CoroutineType):  # Async function
                setattr(_class, k, decorator(v))

        return _class

    return decorate
