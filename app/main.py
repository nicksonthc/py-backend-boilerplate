import asyncio
from http import HTTPStatus
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi_socketio import SocketManager
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    get_redoc_html,
)

from version import __version__
from app.db.init_db import init_db
from app.utils.logger import socketio_logger
from app.core.middleware import ResponseMiddleware
from app.core.log_event_manager import LogEventManager
from app.core.socketio_manager import WmsSocketIO
from app.api.v1 import http_retry_routes, job_routes, order_routes, log_event_routes, auth_routes, setting_routes
from app.core.response import (
    APIResponse,
    BadRequestErrorResponse,
    InternalServerErrorResponse,
    Response,
    UnauthorizedErrorResponse,
    ValidationErrorResponse,
)

EXCLUDE_PATHS = ["/docs", "/openapi", "/swagger-ui", "/redoc", "/v1/log"]
EXCLUDE_TOKEN_CHECK = ["/docs", "/openapi", "/auth", "/swagger-ui", "/redoc", "/log"]
HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Credentials": "False",  # Match your CORS config
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    event_loop = asyncio.get_running_loop()

    # Startup: Initialize database with sample data if needed
    await init_db()

    from app.core.log_manager import LogManager, LogCleanUpService

    # start logging processor
    LogManager.initialize(event_loop)
    LogEventManager.initialize(event_loop)

    # start auto cleaning log
    await LogCleanUpService.initialize()

    ## TODO logging initialize event loop
    from app.core.tcpip.tcp_server import TCPServer

    TCPServer.initialize(event_loop)

    from app.core.http_retry_manager import HttpRetryManager

    await HttpRetryManager.initialize()
    HttpRetryManager.init_cleanup()

    ## TODO hardware coroutine handler here e.g MMS handler for sortation port, label gantry

    ## TODO healthcheck coroutine

    ## TODO recovery handler coroutine

    yield


# Create FastAPI application
app = FastAPI(
    title="Python Backend",
    version=__version__,
    description="FastAPI application with SQLAlchemy, Pydantic, and Socket.IO",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# If using oauth2 verification for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


# To redirect to swagger ui that we served under static folder
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="/static/swagger-ui/pingspace-16x16-favicon.png",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# To redirect to redoc ui that we served under static folder
@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc/redoc.standalone.js",
        redoc_favicon_url="/static/swagger-ui/pingspace-16x16-favicon.png",
    )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add response middleware
app.add_middleware(ResponseMiddleware)

app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(job_routes.router, prefix="/api/v1")
app.include_router(order_routes.router, prefix="/api/v1")
app.include_router(setting_routes.router, prefix="/api/v1")
app.include_router(log_event_routes.router, prefix="/api/v1")
app.include_router(http_retry_routes.router, prefix="/api/v1")

# Socketio setup with debug logging
socketio_logger.info_to_console_only("🚀 Setting up Socket.IO...")
socket_manager = SocketManager(
    app=app, socketio_path="/ws/socket.io", cors_allowed_origins="*", transports=["websocket"]
)


WmsSocketIO.register_socket_events(socket_manager)
socketio_logger.info_to_console_only("✅ WmsSocketIO.register_socket_events() completed successfully")


@app.get("/")
async def index():
    return Response(status=True, code=HTTPStatus.OK, message="Healthy")


@app.get("/health")
async def health_check():
    return Response(status=True, code=HTTPStatus.OK, message="Healthy")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom exception handler for request validation errors (422)"""
    # Format validation errors to match your standard response
    formatted_errors = []
    for error in exc.errors():
        # Extract field path, error message, and input value
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        error_msg = error["msg"]
        input_value = error.get("input", "")
        error_type = error.get("type", "")

        # Format: field_path | error_type | error_msg | input_value
        formatted_error = f"{field_path} | {error_type} | {error_msg} | {input_value}"
        formatted_errors.append(formatted_error)

    return Response(
        status=False,
        code=HTTPStatus.UNPROCESSABLE_ENTITY,
        message="Validation failed",
        error=formatted_errors,
        headers=HEADERS,
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Custom exception handler for unhandled exception"""
    return Response(
        status=False,
        code=HTTPStatus.INTERNAL_SERVER_ERROR,
        message="Internal server error",
        error=str(exc),
        headers=HEADERS,
    )


# Custom OpenAPI function to include custom standard response
def update_openapi():
    """
    NOTE
    APIResponse and ValidationErrorResponse must be use as response model at
    somewhere for generating schema in openai

    Currently using them in test get api
    """

    def _add_standard_response(method: dict, status_code: str, description: str, schema_class: type) -> None:
        """Helper function to add standard response if it doesn't exist or lacks proper schema"""
        responses = method.get("responses", {})

        # Check if response exists and has proper schema
        if status_code not in responses:
            should_add = True
        elif "content" not in responses[status_code]:
            should_add = True
        elif "application/json" not in responses[status_code]["content"]:
            should_add = True
        elif "schema" not in responses[status_code]["content"]["application/json"]:
            should_add = True
        else:
            should_add = False

        # Special handling for 422 - also replace default FastAPI validation error
        if status_code == "422" and not should_add:
            existing_schema = responses[status_code]["content"]["application/json"]["schema"]
            if existing_schema.get("$ref", "") == "#/components/schemas/HTTPValidationError":
                should_add = True

        if should_add:
            responses[status_code] = {
                "description": description,
                "content": {
                    "application/json": {
                        "schema": schema_class.model_json_schema(ref_template="#/components/schemas/{model}")
                    }
                },
            }

    # Response configuration mapping
    standard_responses = {
        "200": {
            "description": "Successful Response",
            "schema_class": APIResponse,
        },
        "400": {
            "description": "Bad Request Response",
            "schema_class": BadRequestErrorResponse,
        },
        "401": {
            "description": "Unauthorized Response",
            "schema_class": UnauthorizedErrorResponse,
        },
        "422": {
            "description": "Validation Error",
            "schema_class": ValidationErrorResponse,
        },
        "500": {
            "description": "Internal Server Error",
            "schema_class": InternalServerErrorResponse,
        },
    }

    global app

    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title="Python Backend API",
            version=__version__,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        )

        # Add a security scheme to append an Authorization header
        app.openapi_schema["components"]["securitySchemes"] = {
            "oauth2_password": {
                "type": "oauth2",
                "flows": {"password": {"tokenUrl": "api/v1/auth/token", "scopes": {}}},
            }
        }

        # Add security requirements
        app.openapi_schema["security"] = [{"oauth2_password": []}]

        for path in app.openapi_schema["paths"].values():
            for method in path.values():
                if "responses" not in method:
                    continue

                # Skip adding standard responses for non-JSON content types
                if "200" in method["responses"]:
                    content = method["responses"]["200"].get("content", {})
                    if not any(ct.startswith("application/json") for ct in content.keys()):
                        continue

                # Add all standard responses using the helper function
                for status_code, config in standard_responses.items():
                    _add_standard_response(
                        method=method,
                        status_code=status_code,
                        description=config["description"],
                        schema_class=config["schema_class"],
                    )

    return app.openapi_schema


app.openapi = update_openapi
