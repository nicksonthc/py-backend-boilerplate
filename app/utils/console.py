import sys

from colorama import Fore, Style
from fastapi_socketio import SocketManager

from app.utils.conversion import datetime_console

# Initialize colorama with strip=False to not strip ANSI codes in Docker/CI environments
# init(
#     strip=False if os.environ.get("DOCKER_CONTAINER") else None,
#     convert=False,
#     autoreset=True,
# )


class ConsolePrint:
    @staticmethod
    def task(msg: str):
        print(f"{datetime_console()} {Fore.YELLOW}[Task] {msg}{Style.RESET_ALL}")

    @staticmethod
    def error(msg: str):
        print(f"{datetime_console()} {Fore.RED}[Error] {msg}{Style.RESET_ALL}")

    @staticmethod
    def recv_plc(msg: str):
        print(f"{datetime_console()} {Fore.CYAN}[Recv] {msg}{Style.RESET_ALL}")

    @staticmethod
    def send_plc(msg: str):
        print(f"{datetime_console()} {Fore.BLUE}[Sent] {msg}{Style.RESET_ALL}")

    @staticmethod
    def recv_http(msg: str):
        print(f"{datetime_console()} {Fore.GREEN}[Http] {msg}{Style.RESET_ALL}")

    @staticmethod
    def socketio(msg: str):
        print(f"{datetime_console()} {Fore.MAGENTA}[Socket] {msg}{Style.RESET_ALL}")

    @staticmethod
    def health(msg: str):
        print(f"{datetime_console()} {Fore.LIGHTYELLOW_EX}[Health] {msg}{Style.RESET_ALL}")


class ConsoleLogger:
    def __init__(self, socket_manager: SocketManager):
        self.socket_manager = socket_manager
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = self
        sys.stderr = self

    async def emit_console_event(self, message: str):
        """Emit the captured console output to the 'console' event."""
        await self.socket_manager.emit("console", {"message": message})

    def write(self, message):
        if message.strip():  # Avoid emitting empty lines
            # Emit the message asynchronously
            import asyncio

            loop = asyncio.get_event_loop()
            if not loop.is_running():
                return
            asyncio.create_task(self.emit_console_event(message))

        # Still write to the original stdout/stderr
        self.stdout.write(message)

    def flush(self):
        self.stdout.flush()
        self.stderr.flush()
