import asyncio
from collections import defaultdict
from http import HTTPMethod
from pydantic import HttpUrl
from time import time
from typing import Any, Callable, Coroutine, DefaultDict, List, Optional

import httpx
from colorama import Fore, Style
from dateutil.relativedelta import relativedelta

from app.controllers.http_retry_controller import HttpRetryController
from app.core.http_headers_manager import HttpHeadersManager
from app.models.schemas.http_retry_schema import HttpRetryCreate, HttpRetryOut
from app.utils.logger import send_http_logger
from app.utils.scheduler import scheduler

client = httpx.AsyncClient()
controller = HttpRetryController()


class HttpRetryManager:
    lock = asyncio.Lock()
    is_completed: DefaultDict[int, asyncio.Future] = defaultdict(asyncio.Future)

    @classmethod
    async def create(
        cls,
        method: HTTPMethod,
        url: HttpUrl,
        payload: dict,
        headers: dict = {},
        timeout: int = 3,
        retry_limit: int = 60,
        retry_interval: int = 5,
        reference: dict = {},
        get_pred_ids: Optional[Callable[[], Coroutine[Any, Any, List[int]]]] = None,
    ):
        async with cls.lock:
            data = await controller.create_http_retry(
                HttpRetryCreate(
                    method=method,
                    url=url,
                    timeout=timeout,
                    payload=payload,
                    headers=HttpHeadersManager.wrap_headers(headers),
                    reference=reference,
                    retry_limit=retry_limit,
                    retry_interval=retry_interval,
                    pred_ids=await get_pred_ids() if get_pred_ids else [],
                )
            )
            asyncio.create_task(cls.emit(cls.is_completed[data.id], data))

    @staticmethod
    async def read(id: int):
        return await controller.read_http_retry(id)

    @staticmethod
    def read_incompleted():
        return controller.get_incompleted_http_retry()

    @classmethod
    async def delete(cls, id: int):
        if fut := cls.is_completed.pop(id, None):
            fut.set_result(True)
        await controller.delete_http_retry(id)

    @classmethod
    async def emit(cls, is_completed: asyncio.Future, data: HttpRetryOut):
        await asyncio.gather(
            *(dependency for pred_id in data.pred_ids if (dependency := cls.is_completed.get(pred_id)))
        )
        while not is_completed.done():
            try:
                from app.core.circuit_breaker import CircuitBreaker

                if CircuitBreaker.is_db_down():
                    send_http_logger.warning_to_console_only(f"DB is down. Skipping HttpRetry(id={data.id})")
                    await asyncio.sleep(CircuitBreaker.suggest_retry_interval)
                    continue

                created_at = time()
                response = res_body = None
                url = str(data.url)
                response = await client.request(
                    method=data.method, url=url, headers=data.headers, data=data.payload, timeout=data.timeout
                )
                res_body = response.json()
                response.raise_for_status()
                await controller.complete_http_retry(data.id, res_body)
                cls.is_completed.pop(data.id, is_completed).set_result(True)
                send_http_logger.info_to_console_only(
                    f'"{Style.BRIGHT}{data.method} {url}{Style.RESET_ALL}" '
                    f"{data.payload} "
                    f"{int((time() - created_at) * 1000)}ms "
                    f"{Fore.GREEN}{response.status_code}{Fore.RESET} "
                )
                return

            except Exception as e:
                attempts = await controller.incr_http_retry_attempts(data.id)
                if response:
                    status_code = response.status_code
                else:
                    status_code = "???"
                    res_body = e.__repr__()
                send_http_logger.error_to_console_only(
                    f"HttpRetry(id={data.id}) "
                    f'"{Style.BRIGHT}{data.method} {url}{Style.RESET_ALL}" '
                    f"{data.payload} "
                    f"{int((time() - created_at) * 1000)}ms "
                    f"{Fore.RED}{status_code}{Fore.RESET} "
                    f"{res_body}"
                )
                if attempts > data.retry_limit:
                    return
                await asyncio.sleep(data.retry_interval)

    @classmethod
    async def initialize(cls):
        async with cls.lock:
            for id in sorted(cls.is_completed, reverse=True):
                fut = cls.is_completed.pop(id)
                fut.set_result(True)

            async for data in controller.get_incompleted_http_retry():
                asyncio.create_task(cls.emit(cls.is_completed[data.id], data))

    @staticmethod
    def init_cleanup():
        scheduler.add_job(controller.clean_http_retry, "cron", day=1, hour=0, minute=0, args=[relativedelta(months=6)])
