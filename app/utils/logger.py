import logging

from colorama import Fore, Style
from uvicorn.logging import ColourizedFormatter

from app.core.log_manager import LogManager


class Formatter(ColourizedFormatter):

    def __init__(self, fore: str):
        self.fore = fore
        super().__init__("%(levelprefix)s %(asctime)s - %(name)s - %(message)s", "%d %b %H:%M:%S")

    def format(self, record):
        record.msg = f"{self.fore}{record.getMessage()}{Style.RESET_ALL}"
        return super().format(record)


class Logger(logging.Logger):

    def __init__(self, name: str, level=0, fore: str = Fore.WHITE) -> None:
        super().__init__(name, level)
        formatter = Formatter(fore)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(level)
        self.addHandler(handler)
        self.log_manager = LogManager(name)

    def info(self, msg: str):
        self.info_to_console_only(msg)
        self.info_to_db_only(msg)

    def warning(self, msg: str):
        self.warning_to_console_only(msg)
        self.warning_to_db_only(msg)

    def error(self, msg: str):
        self.error_to_console_only(msg)
        self.error_to_db_only(msg)

    def info_to_db_only(self, msg: str):
        self.log_manager.info(msg)

    def warning_to_db_only(self, msg: str):
        self.log_manager.warning(msg)

    def error_to_db_only(self, msg: str):
        self.log_manager.error(msg)

    def info_to_console_only(self, msg: str):
        return super().info(msg)

    def warning_to_console_only(self, msg: str):
        return super().warning(msg)

    def error_to_console_only(self, msg: str):
        return super().error(msg)


task_logger = Logger("Task", fore=Fore.YELLOW)
recv_plc_logger = Logger("RecvPlc", fore=Fore.CYAN)
send_plc_logger = Logger("SendPlc", fore=Fore.BLUE)
send_http_logger = Logger("SendHttp")
recv_http_logger = Logger("RecvHttp")
socketio_logger = Logger("Socketio", fore=Fore.MAGENTA)
health_logger = Logger("Health", fore=Fore.LIGHTYELLOW_EX)
