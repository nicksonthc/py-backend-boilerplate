from sqlalchemy import text
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import CONFIG
from app.utils.logger import health_logger


async def init_db():
    from app.db.session import engine
    from app.models.entities import http_retry_model, log_model, job_model, order_model, setting_model

    # Connect to postgres database to check if target database exists
    postgres_url = CONFIG.POSTGRES_DATABASE_URL.replace(f"/{CONFIG.POSTGRES_DB}", "/postgres")
    master_engine = create_async_engine(postgres_url)

    async with master_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"), {"dbname": CONFIG.POSTGRES_DB}
        )
        if result.scalar_one_or_none() is None:
            await conn.execute(text(f'CREATE DATABASE "{CONFIG.POSTGRES_DB}"'))
            health_logger.info_to_console_only(f"✅ Database {CONFIG.POSTGRES_DB} created.")
        else:
            health_logger.info_to_console_only(f"✅ Database {CONFIG.POSTGRES_DB} already exists.")

    await master_engine.dispose()

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        health_logger.info_to_console_only("✅ Tables created.")
