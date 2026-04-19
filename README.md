# Air Quality Monitoring Pipeline

## Overview
A real-time data engineering project that collects, processes, and visualizes air quality data for Indian cities.

---

## Tech Stack

- Kafka & Zookeeper (Streaming)
- Python (Producer & Consumer)
- MySQL (Storage)
- Streamlit (Dashboard)
- Docker (Infrastructure)

---

## Features

- Real-time AQI data ingestion
- Kafka-based streaming pipeline
- Automatic data cleanup (last 2 hours retention)
- City-based AQI search
- Live dashboard with:
  - AQI indicator scale
  - Pollutant breakdown
  - Last 2 hours data (10-min interval)

---

## Project Structure
air_quality_pipeline/
│
├── kafka_pipeline/
│ ├── producer.py
│ ├── consumer.py
│
├── processing/
│ └── transform.py
│
├── storage/
│ └── db.py
│
├── dashboard/
│ └── app.py
│
├── data/
│ ├── raw/
│ └── processed/
│
├── config/
│ └── config.py
│
├── docker-compose.yml
├── requirements.txt
├── README.md

---

## Setup Instructions

### 1. Clone repo

git clone https://github.com/hr-agarwal/air-quality-pipeline.git

cd air-quality-pipeline


---

### 2. Create virtual environment

python -m venv venv
venv\Scripts\activate # Windows


---

### 3. Install dependencies

pip install -r requirements.txt


---

### 4. Start Kafka & Zookeeper

docker-compose up -d


---

### 5. Run Producer

python kafka_pipeline/producer.py


---

### 6. Run Consumer

python -m kafka_pipeline.consumer


---

### 7. Run Dashboard

streamlit run dashboard/app.py


---

## Environment Variables

Create `.env` file:


API_KEY=your_api_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=air_quality
DB_PORT=3306
KAFKA_BROKER=localhost:9092
TOPIC=air-quality


---

## Notes

- Data older than 2 hours is automatically deleted
- AQI values are mapped from OpenWeather index to standard AQI scale
- Dashboard auto-refreshes every 10 seconds

---

## Future Improvements

- Fully automated scheduler (no manual fetch)
- Deployment on cloud (AWS/GCP)
- Alerts for hazardous AQI
- Historical analytics

---

## Author

Harsh Raj Agarwal
