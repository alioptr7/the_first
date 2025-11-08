import psycopg

try:
    conn = psycopg.connect('postgresql://user:password@localhost:5433/response_db')
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM users")
    user_count = cur.fetchone()[0]
    print(f'Number of users: {user_count}')
    
    cur.execute("SELECT COUNT(*) FROM incoming_requests")
    request_count = cur.fetchone()[0]
    print(f'Number of incoming requests: {request_count}')
    
    cur.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
