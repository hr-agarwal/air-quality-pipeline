import os
import json
import pandas as pd
from datetime import datetime

from storage.db import get_connection, create_table

RAW_PATH = "data/raw"
OUTPUT_PATH = "data/processed/air_quality.csv"


def extract_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    entry = data["data"]["list"][0]

    return {
        "timestamp": datetime.fromisoformat(data["timestamp"]),
        "city": data.get("city", "unknown"),
        "aqi": entry["main"]["aqi"],
        "pm2_5": entry["components"].get("pm2_5"),
        "pm10": entry["components"].get("pm10"),
        "co": entry["components"].get("co"),
        "no2": entry["components"].get("no2"),
        "o3": entry["components"].get("o3"),
        "so2": entry["components"].get("so2")
    }


def load_to_db(df):
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO air_quality 
            (timestamp, city, aqi, pm2_5, pm10, co, no2, o3, so2)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row["timestamp"],
            row["city"],
            int(row["aqi"]) if pd.notna(row["aqi"]) else None,
            row["pm2_5"],
            row["pm10"],
            row["co"],
            row["no2"],
            row["o3"],
            row["so2"]
        ))

    conn.commit()
    cur.close()
    conn.close()


def process_all_files():
    records = []

    for root, _, files in os.walk(RAW_PATH):
        for file in files:
            if file.endswith(".json"):
                path = os.path.join(root, file)

                try:
                    record = extract_data(path)
                    records.append(record)
                except Exception as e:
                    print(f"Error in {file}: {e}")

    if not records:
        print("No data found.")
        return

    df = pd.DataFrame(records)

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print("Processed data saved to CSV")

    create_table()
    load_to_db(df)

    print("Data inserted into MySQL")


if __name__ == "__main__":
    process_all_files()