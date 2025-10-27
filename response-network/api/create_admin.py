from sqlalchemy import create_engine, text
import bcrypt

# Database connection settings
DB_USER = "user"
DB_PASS = "password"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "response_db"

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_admin_user():
    # Create database engine
    engine = create_engine(DATABASE_URL)
    
    # Hash the password
    password = "admin".encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt).decode('utf-8')
    
    # SQL query to insert admin user
    sql = text("""
        INSERT INTO users (email, hashed_password, is_active, is_admin, full_name)
        VALUES (:email, :password, true, true, 'Admin User')
        ON CONFLICT (email) DO UPDATE 
        SET hashed_password = :password, is_active = true, is_admin = true
    """)
    
    try:
        with engine.connect() as conn:
            conn.execute(sql, {"email": "admin@example.com", "password": hashed_password})
            conn.commit()
            print("Admin user created/updated successfully!")
    except Exception as e:
        print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user()