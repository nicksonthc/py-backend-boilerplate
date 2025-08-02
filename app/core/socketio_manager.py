import asyncio
from fastapi_socketio import SocketManager
from app.utils.logger import socketio_logger


class WmsSocketIO:

    socket_manager = None

    # Debouncing variables and timers
    _debounce_timers = {}
    _debounce_pending = {}
    _default_debounce_ms = 2000  # Default debounce period (2 seconds)

    @classmethod
    async def debounce(cls, event_name, emit_func, debounce_ms=None, data=None):
        """
        Generic debounce method for socket emissions.

        Args:
            event_name: Unique identifier for this debounced event
            emit_func: Async function that performs the actual emission
            debounce_ms: Optional custom debounce period in milliseconds
        """
        debounce_ms = debounce_ms or cls._default_debounce_ms

        # Cancel existing timer if any
        if event_name in cls._debounce_timers and cls._debounce_timers[event_name] is not None:
            cls._debounce_timers[event_name].cancel()

        # Set pending flag
        cls._debounce_pending[event_name] = True

        # Define the actual emission function
        async def _do_emit():
            if cls._debounce_pending.get(event_name, False):
                await emit_func(data)
                cls._debounce_pending[event_name] = False
                cls._debounce_timers[event_name] = None

        # Set a new timer
        cls._debounce_timers[event_name] = asyncio.create_task(cls._delayed_execution(_do_emit, debounce_ms / 1000))

    @staticmethod
    async def _delayed_execution(func, delay_seconds):
        """Helper method for delayed execution with debouncing"""
        await asyncio.sleep(delay_seconds)
        await func()

    @staticmethod
    def register_socket_events(sm: SocketManager):

        # Store the socket manager
        WmsSocketIO.socket_manager = sm

        @sm.on("connect")
        async def handle_connect(sid, environ):
            socketio_logger.info_to_console_only(f"🟢 Client connected: {sid}")
            socketio_logger.info_to_db_only(f"SocketIO Client connected: {sid}")

            # Send welcome message to client
            if sm:
                await sm.emit("welcome", {"message": f"Welcome! Your session ID is: {sid}"}, to=sid)
                socketio_logger.info_to_console_only(f"📤 Sent welcome message to {sid}")

        @sm.on("disconnect")
        async def handle_disconnect(sid):
            socketio_logger.info_to_console_only(f"🔴 Client disconnected: {sid}")
            socketio_logger.info_to_db_only(f"{sid} disconnected from SIO Server.")

        @sm.on("ping")
        async def handle_ping(sid, data):
            socketio_logger.info_to_console_only(f"🏓 Ping received from {sid}: {data}")
            if sm:
                await sm.emit("pong", {"message": "pong", "timestamp": asyncio.get_event_loop().time()}, to=sid)

        @sm.on("join_room")
        async def handle_join_room(sid, data):
            room = data.get("room", "default")
            socketio_logger.info_to_console_only(f"🚪 {sid} joining room: {room}")
            if sm:
                await sm.enter_room(sid, room)
                await sm.emit("room_joined", {"room": room, "message": f"Joined room: {room}"}, to=sid)

        @sm.on("leave_room")
        async def handle_leave_room(sid, data):
            room = data.get("room", "default")
            socketio_logger.info_to_console_only(f"🚪 {sid} leaving room: {room}")
            if sm:
                await sm.leave_room(sid, room)
                await sm.emit("room_left", {"room": room, "message": f"Left room: {room}"}, to=sid)

    @classmethod
    async def emit(cls, event: str, data, to=None, room=None, callback=None):
        if cls.socket_manager is None:
            socketio_logger.warning_to_console_only("❌ Socket manager is None! Cannot emit event")
            return

        socketio_logger.info_to_console_only(f"📤 Emitting event '{event}' to {to or 'all'}")
        await cls.socket_manager.emit(event, data, to=to, room=room, callback=callback)

    @classmethod
    async def emit_system_availability_update(cls):
        """Emit system availability update"""
        socketio_logger.info_to_console_only("🔄 Emitting system availability update")
        await cls.emit("system-availability", {"status": "available", "timestamp": asyncio.get_event_loop().time()})

    @classmethod
    async def emit_ingress_update(cls):
        # client = cls.runtime_sio_client.get(f"STATION-1", None)
        # if client:
        async def _emit(data):
            socketio_logger.info("Emit ingress-update (debounced)")
            await cls.emit("ingress-update", data)

        await cls.debounce("ingress-update", _emit, 1000)
        await cls.emit_system_availability_update()

    @classmethod
    async def emit_egress_update(cls):
        # client = cls.runtime_sio_client.get(f"STATION-{station_id}", None)
        # if client:
        async def _emit(data):
            socketio_logger.info("Emit egress-update (debounced)")
            await cls.emit("egress-update", data)

        await cls.debounce("egress-update", _emit, 1000)
        await cls.emit_system_availability_update()
