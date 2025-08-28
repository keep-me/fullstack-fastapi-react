#!/usr/bin/env python
"""
Script for optimizing database performance
"""

import asyncio
import logging
import logging.config
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import db_manager, get_session

sys.path.append(str(Path(__file__).resolve().parents[2]))

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger("app.optimize_db")


async def analyze_tables(session: AsyncSession) -> None:
    """
    Analyze database tables to update statistics for query optimizer

        Args:
            session: Database session

    """
    logger.info("Analyzing database tables")
    await session.execute(text("ANALYZE VERBOSE"))
    logger.info("Table analysis completed")


async def vacuum_tables() -> None:
    """
    Vacuum database tables to reclaim storage and update statistics.

        This operation runs in autocommit mode, outside of a transaction.
    """
    logger.info("Vacuuming database tables")
    try:
        engine = db_manager.engine
        async with engine.connect() as connection:
            await connection.execution_options(isolation_level="AUTOCOMMIT")
            await connection.execute(text("VACUUM ANALYZE"))
        logger.info("Vacuum completed")
    except Exception as e:
        logger.error(f"Error during vacuum: {e}")
        logger.info("Skipping vacuum operation")


async def check_slow_queries(session: AsyncSession) -> list[dict]:
    """
    Check for slow queries in PostgreSQL stats

        Args:
            session: Database session

        Returns:
            List of slow queries with execution stats

    """
    logger.info("Checking for slow queries")

    result = await session.execute(
        text(
            """
        SELECT EXISTS (
            SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements'
        )
        """
        ),
    )
    extension_exists = result.scalar()

    if not extension_exists:
        logger.info(
            "pg_stat_statements extension is not enabled. Skipping slow query analysis.",
        )
        logger.info("To enable it, run: CREATE EXTENSION pg_stat_statements;")
        return []

    result = await session.execute(
        text(
            """
        SELECT query, calls, total_time, mean_time, rows
        FROM pg_stat_statements
        ORDER BY mean_time DESC
        LIMIT 10
        """
        ),
    )
    slow_queries = [dict(row) for row in result]

    if slow_queries:
        logger.info(f"Found {len(slow_queries)} slow queries")
        for i, query in enumerate(slow_queries, 1):
            logger.info(
                f"Slow query #{i}: mean_time={query['mean_time']}ms, calls={query['calls']}",
            )
    else:
        logger.info("No slow queries found")

    return slow_queries


async def create_missing_indexes(session: AsyncSession) -> None:
    """
    Create missing indexes based on query patterns

        Args:
            session: Database session

    """
    logger.info("Checking for missing indexes")
    result = await session.execute(
        text(
            """
        SELECT 
            relname AS table_name,
            schemaname AS schema_name,
            seq_scan,
            idx_scan,
            seq_scan - idx_scan AS difference
        FROM 
            pg_stat_user_tables
        WHERE 
            seq_scan > idx_scan
            AND seq_scan > 1000
        ORDER BY 
            difference DESC
        LIMIT 5
        """
        ),
    )

    tables_needing_indexes = [dict(row._mapping) for row in result]

    if tables_needing_indexes:
        logger.info(
            f"Found {len(tables_needing_indexes)} tables that might need indexes",
        )
        for table in tables_needing_indexes:
            logger.info(
                f"Table {table['table_name']} has high sequential scans: {table['seq_scan']}",
            )
    else:
        logger.info("No tables with missing indexes detected")


async def main() -> None:
    """
    Main function to run database optimizations
    """
    logger.info(f"Starting database optimization for {settings.POSTGRES_DB}")

    try:
        async for session in get_session():
            await check_slow_queries(session)
            await create_missing_indexes(session)
            await analyze_tables(session)

        await vacuum_tables()

        logger.info("Database optimization completed successfully")
    except Exception as e:
        logger.error(f"Error during database optimization: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
