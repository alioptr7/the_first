import psycopg

try:
    conn = psycopg.connect('postgresql://user:password@localhost:5433/response_db')
    cur = conn.cursor()
    
    # Get column names of users table
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'users'
        ORDER BY ordinal_position;
    """)
    
    print("Columns in users table:")
    for row in cur.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
