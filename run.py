import uvicorn
from uvicorn.protocols.http.h11_impl import H11Protocol
from app.core.config import CONFIG
import logging


class CustomAccessLogger:
    def __init__(self, logger):
        self.logger = logger

    def __call__(self, scope, message, transport):
        if scope["type"] == "http" and scope["method"] != "GET":
            # Skip logging for /v1/log path
            if scope["path"] == "/v1/log":
                return
            client = scope.get("client")
            self.logger.info(f"{scope['method']} {scope['path']} from {client}")


# Add the project root to Python path
if __name__ == "__main__":
    logger = logging.getLogger("uvicorn.access")
    logger.setLevel(logging.INFO)

    # Start server with custom access log
    uvicorn.run(
        "app.main:app",
        host=CONFIG.API_HOST,
        port=CONFIG.API_PORT,
        access_log=False,  # enable access logging
        log_level="info",  # enable info level logging
        reload=True,  # enable auto-reload for development
    )

    # Monkey patch uvicorn to use our custom access logger
    # H11Protocol.access_logger = CustomAccessLogger(logger)
