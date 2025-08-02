from fastapi import Depends
from typing import AsyncGenerator, Optional, Annotated
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import CONFIG
from app.utils.logger import Logger

logger = Logger("db_session_log")


def create_engine(database_url: Optional[str] = None):
    """Create database engine with optional URL override."""
    url = database_url or CONFIG.POSTGRES_DATABASE_URL

    return create_async_engine(
        url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
        # Connection arguments for PostgreSQL
        connect_args={
            "command_timeout": 3,  # PostgreSQL equivalent of timeout
            "server_settings": {
                "application_name": "backend-server",  # Optional: helps identify connections
            },
        },
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
    )


# Create default engine
engine = create_engine()


# Create session factory for async sessions
def create_session_factory(engine_instance=None):
    """Create a session factory with optional engine override."""
    target_engine = engine_instance or engine
    return async_sessionmaker(
        target_engine, class_=AsyncSession, expire_on_commit=True, autoflush=False, autocommit=False
    )


# Default session factory
SessionLocal = create_session_factory()


# Dependency for getting a database session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides an async database session
    that is automatically closed when the request is finished.

    Uses MSSQL for production.

    ✅ FastAPI dependency injection - Depends(get_session)
    ✅ FastAPI route handlers - automatic lifecycle management
    ✅ When you need to yield multiple values (though rare for DB sessions)
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error_to_console_only(f"get_session raised exception: {e}")
            # TODO log to file system
            raise
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]


# Async context manager for direct session usage
@asynccontextmanager
async def get_session_context(
    session_factory: Optional[async_sessionmaker] = None,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async context manager for database sessions.

    Usage:
    - ✅ Background tasks (like your log manager)
    - ✅ Standalone async functions outside FastAPI
    - ✅ Manual session management with explicit control
    - ✅ When you want clean async with syntax

    Example:
        async with get_session_context() as session:
            await session.execute(...)
    """
    factory = session_factory or SessionLocal
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error_to_console_only(f"get_session_context raised exception: {e}")
            raise
        finally:
            await session.close()
