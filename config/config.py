import os
from dotenv import load_dotenv

# Get absolute path of project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env explicitly
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_KEY = os.getenv("API_KEY")
LAT = float(os.getenv("LAT")) if os.getenv("LAT") else None
LON = float(os.getenv("LON")) if os.getenv("LON") else None

BASE_URL = os.getenv("BASE_URL")

KAFKA_BROKER = os.getenv("KAFKA_BROKER")
TOPIC = os.getenv("TOPIC")

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")