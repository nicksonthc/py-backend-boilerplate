from http import HTTPStatus
import json

from time import time
from typing import Any, Awaitable, Callable
from colorama import Fore, Style
from fastapi import Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.http_headers_manager import HttpHeadersManager
from app.core.response import APIResponse, Response as StandardResponse, UnauthorizedErrorResponse
from app.utils.logger import recv_http_logger


UNKNOWN_USER = "UNKNOWN"


class ResponseMiddleware(BaseHTTPMiddleware):
    EXCLUDE_PATHS = ["/docs", "/openapi", "/swagger-ui", "/redoc", "/v1/log", "/"]
    EXCLUDE_TOKEN_CHECK = ["/docs", "/openapi", "/auth", "/swagger-ui", "/redoc", "/log"]
    HEADERS = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Credentials": "False",  # Match your CORS config
    }

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response | StreamingResponse]]
    ) -> Response:
        # TODO add token checking here for login validation
        # TODO extract username from here and add into logging so can track user action
        HttpHeadersManager.set_headers(request.headers)

        # filter OPTIONS method for token checking
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response

        # filter excluded paths
        if any(path in request.scope["path"] for path in self.EXCLUDE_PATHS):
            response = await call_next(request)
            return response

        from app.core.circuit_breaker import CircuitBreaker

        if CircuitBreaker.is_db_down():
            return StandardResponse(
                api_response_model=APIResponse(
                    status=False,
                    code=HTTPStatus.SERVICE_UNAVAILABLE,
                    message=f"DB is down since {CircuitBreaker.db_down_start_time} due to {CircuitBreaker.db_down_reason}. Will not allowed any request. Please try again later.",
                ),
                headers=self.HEADERS,
            )

        # handle incoming request
        client = request.client
        request_body = await request.body()
        try:
            decoded = request_body.decode()
        except UnicodeDecodeError:
            decoded = str()

        # handle outgoing response
        created_at = time()
        username, response = self.check_token(request)
        if response:
            elapsed = int((time() - created_at) * 1000)
            recv_http_logger.error(
                f"{client.host}:{client.port} "
                f'"{Style.BRIGHT}{request.method} {request.url.path}{Style.RESET_ALL}" '
                f"{elapsed}ms "
                f"{username} "
                f"{Fore.RED}{response.status_code}{Fore.RESET} "
                f"{decoded}"
            )
            return response

        response = await call_next(request)
        elapsed = int((time() - created_at) * 1000)
        if response.status_code == HTTPStatus.OK.value:
            recv_http_logger.info(
                f"{client.host}:{client.port} "
                f'"{Style.BRIGHT}{request.method} {request.url.path}{Style.RESET_ALL}" '
                f"{elapsed}ms "
                f"{username} "
                f"{Fore.GREEN}{response.status_code}{Fore.RESET} "
            )
            return response

        res_body = b""
        async for chunk in response.body_iterator:
            res_body += chunk

        recv_http_logger.error(
            f"{client.host}:{client.port} "
            f'"{Style.BRIGHT}{request.method} {request.url.path}{Style.RESET_ALL}" '
            f"{elapsed}ms "
            f"{username} "
            f"{Fore.RED}{response.status_code}{Fore.RESET} "
            f"{decoded} "
            f"{res_body.decode()}"
        )

        # need to use this class instead of straight return because we already iterate through the iterator
        # the content of body is changed
        return Response(
            content=res_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    def check_token(self, request: Request):
        username = UNKNOWN_USER
        response = None
        try:
            if any(path in request.scope["path"] for path in self.EXCLUDE_TOKEN_CHECK):
                return

            from app.auth.token import TokenManager, ExpiredSignatureError, InvalidTokenError

            authorization = request.headers.get("Authorization")

            if not authorization:
                response = StandardResponse(
                    api_response_model=UnauthorizedErrorResponse(message="No authorization token provided"),
                    headers=self.HEADERS,
                )
                return

            try:
                token = authorization.split(" ")[1]
                payload = TokenManager.verify_token(token)
                username = payload.get("username", UNKNOWN_USER) if payload else UNKNOWN_USER
            except ExpiredSignatureError:
                response = StandardResponse(
                    api_response_model=UnauthorizedErrorResponse(message="Token has expired"), headers=self.HEADERS
                )
            except Exception:
                response = StandardResponse(
                    api_response_model=UnauthorizedErrorResponse(message="Invalid Token Provided"), headers=self.HEADERS
                )

        finally:
            return username, response
