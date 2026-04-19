import json
import time
import requests
from datetime import datetime
from kafka import KafkaProducer

from config.config import BASE_URL, API_KEY, KAFKA_BROKER, TOPIC


def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5
    )


def get_coordinates(city):
    url = "http://api.openweathermap.org/geo/1.0/direct"

    params = {
        "q": city + ",IN",
        "limit": 1,
        "appid": API_KEY
    }

    res = requests.get(url, params=params).json()

    if not res:
        return None, None

    return res[0]["lat"], res[0]["lon"]


def fetch_air_quality(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }

    res = requests.get(BASE_URL, params=params)

    if res.status_code != 200:
        return None

    return res.json()


def send_data(city):
    producer = create_producer()

    lat, lon = get_coordinates(city)

    if lat is None:
        print("City not found")
        return

    data = fetch_air_quality(lat, lon)

    if data is None:
        print("API error")
        return

    message = {
        "timestamp": datetime.utcnow().isoformat(),
        "city": city,
        "location": {"lat": lat, "lon": lon},
        "data": data
    }

    producer.send(TOPIC, value=message)
    producer.flush()

    print(f"Sent data for {city}")