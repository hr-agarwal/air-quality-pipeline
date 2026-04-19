import mysql.connector
from datetime import datetime, timedelta

from config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT


def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=int(DB_PORT)
    )


def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS air_quality (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            city VARCHAR(50),
            aqi INT,
            pm2_5 FLOAT,
            pm10 FLOAT,
            co FLOAT,
            no2 FLOAT,
            o3 FLOAT,
            so2 FLOAT
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# ✅ FIXED CLEANUP FUNCTION
def cleanup_old_data(hours=2):
    conn = get_connection()
    cur = conn.cursor()

    # Calculate cutoff time in Python (more reliable than SQL NOW())
    cutoff_time = datetime.now() - timedelta(hours=hours)

    cur.execute("""
        DELETE FROM air_quality
        WHERE timestamp < %s
    """, (cutoff_time,))

    conn.commit()
    cur.close()
    conn.close()