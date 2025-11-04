from sqlalchemy import create_engine, text
from core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_CONNECTION_URL.replace("asyncpg", "psycopg2"))

# Update profile types
with engine.connect() as connection:
    # Update admin user
    connection.execute(
        text("UPDATE users SET profile_type = 'admin' WHERE username = 'admin'")
    )
    
    # Update basic user
    connection.execute(
        text("UPDATE users SET profile_type = 'basic' WHERE username = 'basic_user'")
    )
    
    # Update premium user
    connection.execute(
        text("UPDATE users SET profile_type = 'premium' WHERE username = 'premium_user'")
    )
    
    connection.commit()

print("Profile types updated successfully!")