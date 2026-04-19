from storage.db import get_connection

conn = get_connection()
print("Connected to MySQL")
conn.close()