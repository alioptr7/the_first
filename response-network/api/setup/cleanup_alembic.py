"""Clean up alembic state for fresh migration."""
import asyncio
from sqlalchemy import text
from core.dependencies import get_db

async def cleanup_alembic():
    """Drop alembic_version table."""
    async with get_db() as db:
        # Drop alembic_version table
        await db.execute(text("DROP TABLE IF EXISTS alembic_version"))
        await db.commit()
        print("Dropped alembic_version table")

if __name__ == "__main__":
    asyncio.run(cleanup_alembic())