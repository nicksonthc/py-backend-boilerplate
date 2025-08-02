import asyncio
from typing import Dict, List, Tuple, Optional, ClassVar

# Type alias for address
ADDR = Tuple[str, int]


class AsyncTCPClient:
    """
    A TCP client implementation using asyncio.
    This class manages client connections and provides methods to send messages.
    """

    # Class variable to store all client instances
    clients: ClassVar[Dict[ADDR, "AsyncTCPClient"]] = {}

    def __init__(self, addr: ADDR, writer: asyncio.StreamWriter):
        """
        Initialize a new TCP client.

        Args:
            addr: Tuple of (host, port) representing the client's address
            writer: StreamWriter object for sending data to the client
        """
        self.addr = addr
        self.writer = writer
        self.is_connected = True

    def send(self, message: str) -> None:
        """
        Send a message to the client.

        Args:
            message: The string message to send
        """
        if not self.is_connected:
            raise ConnectionError(f"Client {self.addr} is not connected")

        try:
            self.writer.write(message.encode("utf-8"))
            asyncio.create_task(self.writer.drain())
        except Exception as e:
            self.is_connected = False
            raise ConnectionError(f"Failed to send message to {self.addr}: {str(e)}")

    def close(self) -> None:
        """Close the connection to the client."""
        if self.is_connected:
            self.writer.close()
            self.is_connected = False

    @classmethod
    def add_client(cls, addr: ADDR, writer: asyncio.StreamWriter) -> "AsyncTCPClient":
        """
        Add a new client or update an existing one.

        Args:
            addr: Client address tuple (host, port)
            writer: StreamWriter for the client

        Returns:
            The client instance
        """
        # If client already exists, close the old connection
        if addr in cls.clients:
            cls.clients[addr].close()

        # Create and store new client
        client = cls(addr, writer)
        cls.clients[addr] = client
        return client

    @classmethod
    def remove_client(cls, addr: ADDR) -> None:
        """
        Remove a client by address.

        Args:
            addr: Client address tuple (host, port)
        """
        if addr in cls.clients:
            cls.clients[addr].close()
            cls.clients.pop(addr, None)

    @classmethod
    def get_client(cls, addr: ADDR) -> Optional["AsyncTCPClient"]:
        """
        Get a client by address.

        Args:
            addr: Client address tuple (host, port)

        Returns:
            The client instance or None if not found
        """
        return cls.clients.get(addr)

    @classmethod
    def get_client_by_ip(cls, ip: str) -> Optional["AsyncTCPClient"]:
        """
        Get a client by IP address.

        Args:
            ip: Client IP address

        Returns:
            The client instance or None if not found
        """
        for client in cls.clients.values():
            if client.addr[0] == ip:
                return client
        return None

    @classmethod
    def get_all_clients(cls) -> List["AsyncTCPClient"]:
        """
        Get all connected clients.

        Returns:
            List of all client instances
        """
        return list(cls.clients.values())

    @classmethod
    def clear_all_clients(cls) -> None:
        """
        Clear all connected clients.
        """
        for client in cls.clients.values():
            client.close()
        cls.clients.clear()
