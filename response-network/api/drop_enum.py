from sqlalchemy import create_engine, text

def main():
    engine = create_engine('postgresql://user:password@localhost:5433/response_db')
    with engine.connect() as conn:
        conn.execute(text("DROP TYPE IF EXISTS accesstype CASCADE;"))
        conn.commit()

if __name__ == "__main__":
    main()