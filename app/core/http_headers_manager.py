import asyncio
import uuid
from bisect import bisect
from collections import OrderedDict
from contextvars import ContextVar
from datetime import datetime, timedelta
from functools import wraps
from http import HTTPStatus
from typing import Awaitable, Callable, Tuple

from app.core.response import Response
from app.utils.conversion import get_current_utc_time
from app.utils.scheduler import scheduler

CORRELATION_KEY = "X-Correlation-ID"
IDEMPOTENCY_KEY = "X-Idempotency-ID"


class HttpHeadersManager:

    correlation_id_ctx = ContextVar("correlation_id", default=None)
    idempotency_id_ctx = ContextVar("idempotency_id", default=None)

    @classmethod
    def set_headers(cls, headers: dict):
        cls.correlation_id_ctx.set(headers.get(CORRELATION_KEY))
        cls.idempotency_id_ctx.set(headers.get(IDEMPOTENCY_KEY))

    @classmethod
    def wrap_headers(cls, headers: dict):
        if not headers.get(CORRELATION_KEY):
            headers[CORRELATION_KEY] = cls.correlation_id_ctx.get() or str(uuid.uuid4())
        if not headers.get(IDEMPOTENCY_KEY):
            headers[IDEMPOTENCY_KEY] = str(uuid.uuid4())
        return headers

    @classmethod
    def wrap_idempotency(cls, max_len: int = 20, ttl: timedelta = timedelta(days=1)):
        """
        Decorator to ensure that an endpoint behaves idempotently across repeated calls.

        Example:
        @router.post("/")
        @HttpHeadersManager.wrap_idempotency()
        async def create_http_retry(data: HttpRetryIn):
            await HttpRetryManager.create(**data.model_dump())
            return Response()
        """
        lock = asyncio.Lock()
        responses: OrderedDict[str, Tuple[Response, datetime]] = OrderedDict()

        async def _clean_up():
            expired_at = get_current_utc_time() - ttl
            list_responses = list(responses.items())
            i = bisect(list_responses, expired_at, key=lambda x: x[1][1])
            for response in list_responses[:i]:
                responses.pop(response[0], None)

        scheduler.add_job(_clean_up, "cron", day=1)

        def _decorate(func: Callable[[], Awaitable]):
            @wraps(func)
            async def _func(*args, **kwargs):
                if not (id := cls.idempotency_id_ctx.get()):
                    return await func(*args, **kwargs)

                async with lock:
                    if data := responses.get(id):
                        return data[0]

                    res: Response = await func(*args, **kwargs)
                    if res.status_code == HTTPStatus.OK:
                        responses[id] = res, get_current_utc_time()

                        ids = list(responses)
                        if count := max(len(ids) - max_len, 0):
                            for id in ids[:count]:
                                responses.pop(id, None)
                    return res

            return _func

        return _decorate
