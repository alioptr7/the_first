import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def run_sql(sql: str):
    engine = create_async_engine(
        "postgresql+asyncpg://user:password@localhost:5433/response_db",
        echo=True,
    )
    async with engine.connect() as conn:
        await conn.execute(text(sql))
        await conn.commit()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        sql_command = sys.argv[1]
        asyncio.run(run_sql(sql_command))