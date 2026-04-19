import json
from kafka import KafkaConsumer
from datetime import datetime
import pytz

from config.config import KAFKA_BROKER, TOPIC
from storage.db import get_connection, create_table, cleanup_old_data


def convert_aqi(index):
    mapping = {
        1: 50,
        2: 100,
        3: 150,
        4: 250,
        5: 400
    }
    return mapping.get(index, None)


def insert_into_db(message):
    conn = get_connection()
    cur = conn.cursor()

    entry = message["data"]["list"][0]

    # ✅ FIX 1: Proper UTC → IST conversion
    utc_time = datetime.fromisoformat(message["timestamp"])

    if utc_time.tzinfo is None:
        utc_time = pytz.utc.localize(utc_time)  # ensure UTC aware

    ist = pytz.timezone("Asia/Kolkata")
    local_time = utc_time.astimezone(ist)

    # ✅ FIX 2: Store clean DATETIME (no timezone object)
    local_time = local_time.replace(tzinfo=None)

    aqi_index = entry["main"]["aqi"]
    real_aqi = convert_aqi(aqi_index)

    cur.execute("""
        INSERT INTO air_quality 
        (timestamp, city, aqi, pm2_5, pm10, co, no2, o3, so2)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        local_time,
        message.get("city", "unknown"),
        real_aqi,
        entry["components"].get("pm2_5"),
        entry["components"].get("pm10"),
        entry["components"].get("co"),
        entry["components"].get("no2"),
        entry["components"].get("o3"),
        entry["components"].get("so2")
    ))

    conn.commit()
    cur.close()
    conn.close()


def run_consumer():
    create_table()

    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True
    )

    print("Consumer running... writing to DB")

    for msg in consumer:
        data = msg.value

        try:
            insert_into_db(data)

            # ✅ FIX 3: Controlled cleanup (only older than 2 hours)
            cleanup_old_data(hours=2)

            print(f"Inserted for {data.get('city')}")
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    run_consumer()