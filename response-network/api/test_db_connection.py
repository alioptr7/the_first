import psycopg

try:
    conn = psycopg.connect('postgresql://user:password@localhost:5433/response_db')
    print('Database connection successful')
    
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    count = cur.fetchone()[0]
    print(f'Number of tables in database: {count}')
    
    cur.close()
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
