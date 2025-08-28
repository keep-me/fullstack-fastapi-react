"""
Backend pre-start functionality.
"""

import asyncio
import logging

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import select
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.core.db import DatabaseManager
from app.core.exceptions import DatabaseError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database_if_not_exists() -> None:
    """
    Connects to 'postgres' database and creates database if missing.
    """
    logger.info(f"Checking if database '{settings.POSTGRES_DB}' exists...")

    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_SERVER,
            port=settings.POSTGRES_PORT,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (settings.POSTGRES_DB,)
        )
        if not cur.fetchone():
            logger.info(
                f"Database '{settings.POSTGRES_DB}' does not exist. Creating..."
            )
            cur.execute(f'CREATE DATABASE "{settings.POSTGRES_DB}"')
            logger.info(f"Database '{settings.POSTGRES_DB}' created successfully.")
        else:
            logger.info(f"Database '{settings.POSTGRES_DB}' already exists.")

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error creating database '{settings.POSTGRES_DB}': {e}")
        raise DatabaseError("create_database_failed", str(e))


max_tries = 60 * 5
wait_seconds = 1

db_manager = DatabaseManager()


@retry(
    stop=stop_after_attempt(settings.DB_CONNECTION_RETRY_MAX_TRIES),
    wait=wait_fixed(settings.DB_CONNECTION_RETRY_WAIT_SECONDS),
)
async def init() -> None:
    """
    Check database connection
    """
    try:
        async with db_manager.session_maker() as session:
            await session.execute(select(1))
            logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseError("connection_failed")


async def async_main() -> None:
    """
    Async entry point
    """
    logger.info("Initializing service")
    await init()
    logger.info("Service finished initializing")


def main() -> None:
    """
    Sync entry point for running async code
    """
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
