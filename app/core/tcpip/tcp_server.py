import asyncio
from datetime import datetime
from queue import Queue
from typing import Callable

from app.core.config import CONFIG
from app.core.tcpip.async_tcp_client import AsyncTCPClient, ADDR
from app.core.tcpip.async_tcp_server import AsyncTCPServer
from app.core.log_event_manager import LogEventManager, LogEventCreate
from app.utils.enum import EventDirection, Module
from app.utils.logger import Logger


# Mock logger for TCP server - pending proper LogManager integration
class MockTCPLogger:
    """Mock logger for TCP server operations while LogManager integration is pending"""

    def __init__(self, name: str = "tcp_server"):
        self.name = name

    def info(self, message: str) -> None:
        """Log info message"""
        print(f"[TCP-INFO] {message}")

    def error(self, message: str) -> None:
        """Log error message"""
        print(f"[TCP-ERROR] {message}")

    def warning(self, message: str) -> None:
        """Log warning message"""
        print(f"[TCP-WARNING] {message}")


# Initialize mock logger
# tcp_server_log = MockTCPLogger("tcp_server")
tcp_server_log = Logger("tcp_server_log")


async def mock_disconnect_callback(addr: str | None):
    print(f"Disconnected from {addr}")


# Create a TCPServer class that inherits from our new AsyncTCPServer
# This maintains compatibility with existing code
class TCPServer(AsyncTCPServer):
    message_queue: Queue = Queue()
    client = AsyncTCPClient  # For compatibility with old code

    @classmethod
    def initialize(
        cls,
        event_loop: asyncio.AbstractEventLoop,
        disconnect_callback: Callable = mock_disconnect_callback,
    ):
        super().initialize(
            event_loop,
            AsyncTCPClient,
            CONFIG.TCP_HOST,
            CONFIG.TCP_PORT,
            tcp_server_log.info,
            tcp_server_log.error,
            disconnect_callback,
        )

        if cls.event_loop is not None:
            cls.event_loop.create_task(super().start_server(), name="tcp_server")

    @classmethod
    def validate_connection(cls, ip: str) -> bool:
        return super().validate_connection(ip)

    @classmethod
    def handle_message(cls, client: AsyncTCPClient, message: bytes):

        try:
            decoded_message = message.decode("utf-8")
            if len(decoded_message) == 0:
                # ping client to test connection, catch error if not connected
                client.send("ping")
                return

            for m in cls.split_message(decoded_message):
                msg = m.strip()
                if not msg:
                    continue

                from app.core.circuit_breaker import CircuitBreaker

                if CircuitBreaker.is_db_down():
                    tcp_server_log.warning_to_console_only(f"DB is down. Skipping message: {msg}")
                    continue

                # m = PLCMessageDto(full_msg=msg, client=client)

                # # Reduce terminal pollution
                # if m.command not in ["LOG", "H"]:
                #     ConsolePrint.recv_plc(msg)
                #     EventLogManager.add_recv_plc(m, RunTimeHardware.get_stations_name(m.module, m.device_id))
                # cls.log_info(f"Received message: {msg}")
                split_msg = msg.split(",")
                if split_msg[0] not in [module.value for module in Module]:
                    continue

                if not split_msg[1].isdigit():
                    continue

                station_name = f"{split_msg[0]} {split_msg[1]}"
                module = Module(split_msg[0])
                station_code = int(split_msg[1])

                LogEventManager._add_to_queue(
                    LogEventCreate(
                        station_name=station_name,
                        module=module,
                        station_code=station_code,
                        message_content=msg,
                        direction=EventDirection.RECEIVE,
                    )
                )
                cls.message_queue.put(msg)

        except Exception as e:
            cls.log_error(f"Error handling message: {str(e)}")

    @classmethod
    def send_msg_without_log(cls, ip: str, port: int, msg: str) -> bool:
        addr: ADDR = (ip, port)
        client = cls.client.get_client(addr)

        if not client:
            cls.invalid_msg(addr)
            return False

        try:
            client.send(msg)
            return True
        except Exception as e:
            cls.log_error(f"Error sending message to {addr}: {str(e)}")
            return False
