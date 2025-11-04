import asyncio
from sqlalchemy import create_engine, inspect
from core.config import settings

async def main():
    engine = create_engine(settings.DATABASE_CONNECTION_URL.replace('+asyncpg', ''))
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    for table in tables:
        print(f"Table: {table}")
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  - {column['name']} : {str(column['type'])}")

if __name__ == "__main__":
    asyncio.run(main())
