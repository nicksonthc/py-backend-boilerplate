import asyncio
from dataclasses import dataclass
from queue import Queue
from typing import List, Tuple, Callable, Optional, Any, Dict

from app.core.config import CONFIG
from app.utils.logger import send_plc_logger
from .async_tcp_client import AsyncTCPClient, ADDR


class AsyncTCPServer:
    """
    Asynchronous TCP Server implementation using asyncio.
    Handles client connections and message processing.
    """

    # Class variables
    message_queue: Queue = Queue()
    server: Optional[asyncio.Server] = None
    event_loop: Optional[asyncio.AbstractEventLoop] = None
    log_info: Optional[Callable[[str], None]] = None
    log_error: Optional[Callable[[str], None]] = None
    disconnect_callback: Optional[Callable[[str | None], None]] = None

    @classmethod
    def initialize(
        cls,
        event_loop: asyncio.AbstractEventLoop,
        client_class: type[AsyncTCPClient],
        host: str = CONFIG.TCP_HOST,
        port: int = CONFIG.TCP_PORT,
        log_info: Callable[[str], None] = print,
        log_error: Callable[[str], None] = print,
        disconnect_callback: Callable | None = None,
    ):
        """
        Initialize the TCP server.

        Args:
            event_loop: The asyncio event loop to use
            client_class: The client class to use for connections
            host: The host address to bind to
            port: The port to bind to
            log_info: Function for logging info messages
            log_error: Function for logging error messages
        """
        cls.event_loop = event_loop
        cls.client_class = client_class
        cls.host = host
        cls.port = port
        cls.log_info = log_info
        cls.log_error = log_error
        cls.disconnect_callback = disconnect_callback

    @classmethod
    async def start_server(cls):
        """Start the TCP server and listen for connections."""
        while True:
            try:
                cls.server = await asyncio.start_server(cls.handle_client_connection, cls.host, cls.port)

                cls.log_info(f"TCP Server started on {cls.host}:{cls.port}")
                async with cls.server:
                    await cls.server.serve_forever()

            except asyncio.CancelledError:
                cls.log_info("TCP Server main loop was cancelled")
            except Exception as e:
                cls.log_error(f"Error in TCP Server main loop: {str(e)}")
            finally:
                cls.shutdown()
                cls.log_info("Restarting server......")
                await asyncio.sleep(5)  # Wait before restarting

    @classmethod
    async def handle_client_connection(cls, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Handle a new client connection.

        Args:
            reader: StreamReader for receiving data from the client
            writer: StreamWriter for sending data to the client
        """
        # Get client address
        addr = writer.get_extra_info("peername")
        if not addr:
            cls.log_error("Failed to get client address")
            writer.close()
            return

        # Create client instance
        client = cls.client_class.add_client(addr, writer)
        cls.log_info(f"New connection from {addr}")

        try:
            while True:
                try:
                    data = await reader.read(4096)
                    if not data:
                        break

                    cls.handle_message(client, data)
                except ConnectionResetError:
                    cls.log_info(f"Client {addr} connection reset")
                    break
                except OSError as e:
                    if e.winerror == 64:  # Network name no longer available
                        cls.log_info(f"Client {addr} network name no longer available")
                        break
                    raise

        except asyncio.CancelledError:
            cls.log_info(f"Connection handler for {addr} was cancelled")
        except Exception as e:
            cls.log_error(f"Error handling client {addr}: {str(e)}")
        finally:
            # Clean up
            cls.client_class.remove_client(addr)

            # Handle crane and conveyor disconnections
            if cls.disconnect_callback:
                await cls.disconnect_callback(addr)

            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                cls.log_info(f"Error during connection cleanup for {addr}: {str(e)}")
            cls.log_info(f"Connection from {addr} closed")

    @classmethod
    def split_message(cls, message: str) -> List[str]:
        """
        Split a message by semicolons.

        Args:
            message: The message to split

        Returns:
            List of message parts
        """
        return [m for m in message.split(";") if m]

    @classmethod
    def add_message(cls, full_msg: str):
        """
        Add a message to the queue.
        Used by API or other external modules.

        Args:
            full_msg: The message to add
        """

        cls.message_queue.put(full_msg)

    @classmethod
    def handle_message(cls, client: AsyncTCPClient, message: bytes):
        raise NotImplementedError("This method should be implemented by the subclass")

    @classmethod
    def get_all_clients_addr(cls) -> List[ADDR]:
        """
        Get addresses of all connected clients.

        Returns:
            List of client addresses
        """
        clients = cls.client_class.get_all_clients()
        return [client.addr for client in clients]

    @classmethod
    def send_msg(cls, ip: str, port: int, msg: str) -> bool:
        """
        Send a message to a specific client.

        Args:
            ip: Client IP address
            port: Client port
            msg: Message to send

        Returns:
            True if message was sent successfully, False otherwise
        """
        addr = (ip, port)
        client = cls.client_class.get_client(addr)

        if not client:
            cls.invalid_msg(addr)
            return False

        try:
            client.send(msg)
            send_plc_logger.debug(msg)
            return True
        except Exception as e:
            cls.log_error(f"Error sending message to {addr}: {str(e)}")
            return False

    @classmethod
    def invalid_msg(cls, addr: ADDR):
        """
        Log an invalid message attempt.

        Args:
            addr: The address that was not found
        """
        msg = f"Client {addr} is not connected to WMS."
        cls.log_error(msg)

    @classmethod
    def validate_connection(cls, ip: str) -> bool:
        """
        Validate if a connection exists.

        Args:
            ip: IP address to check

        Returns:
            True if connection exists, False otherwise
        """
        # Check if any client has this IP
        for client in cls.client_class.get_all_clients():
            if client.addr[0] == ip:
                return True
        return False

    @classmethod
    def shutdown(cls):
        """Shutdown the server and close all connections."""
        if cls.server:
            cls.server.close()

        # Close all client connections
        cls.client_class.clear_all_clients()

        cls.log_info("TCP Server shutdown complete")
