import sys
import os
import time
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

from storage.db import get_connection
from kafka_pipeline.producer import send_data


# ---------------- DATA ---------------- #

def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM air_quality", conn)
    conn.close()
    return df


# ---------------- AQI ---------------- #

def aqi_label(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy (Sensitive)"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def aqi_color(aqi):
    if aqi <= 50:
        return "#2ecc71"
    elif aqi <= 100:
        return "#f1c40f"
    elif aqi <= 150:
        return "#e67e22"
    elif aqi <= 200:
        return "#e74c3c"
    elif aqi <= 300:
        return "#8e44ad"
    else:
        return "#7f1d1d"


# Correct segment-based mapping
def get_position(aqi):
    if aqi <= 50:
        return (aqi / 50) * 16.66
    elif aqi <= 100:
        return 16.66 + ((aqi - 50) / 50) * 16.66
    elif aqi <= 150:
        return 33.33 + ((aqi - 100) / 50) * 16.66
    elif aqi <= 200:
        return 50 + ((aqi - 150) / 50) * 16.66
    elif aqi <= 300:
        return 66.66 + ((aqi - 200) / 100) * 16.66
    else:
        return 83.33 + min((aqi - 300) / 200, 1) * 16.66


# ---------------- UI ---------------- #

st.set_page_config(layout="wide")
st.title("🌍 Air Quality Dashboard")

# ---- Input ---- #
col1, col2 = st.columns([3, 1])

with col1:
    city = st.text_input("Enter City (India)", "Delhi")

with col2:
    if st.button("Fetch AQI"):
        send_data(city)
        time.sleep(2)
        st.rerun()


# ---- Load Data ---- #
df = load_data()

if df.empty:
    st.warning("No data available")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

city_df = df[df["city"].str.lower() == city.lower()]

if city_df.empty:
    st.warning("No data for this city")
    st.stop()

latest = city_df.iloc[-1]
aqi = int(latest["aqi"])


# ---------------- MAIN CARD ---------------- #

st.markdown(f"""
<div style="background:linear-gradient(135deg,#1f2937,#374151);
padding:30px;border-radius:20px;color:white;margin-bottom:20px;display:flex;justify-content:space-between;">

<div>
<div style="color:#9ca3af;">Live AQI</div>
<div style="font-size:70px;font-weight:bold;color:{aqi_color(aqi)};">{aqi}</div>
<div style="color:#9ca3af;">AQI (US)</div>
</div>

<div>
<div style="color:#9ca3af;">Air Quality is</div>
<div style="padding:10px 20px;border-radius:10px;background:rgba(255,255,255,0.1);margin-top:5px;">
{aqi_label(aqi)}
</div>
</div>

<div>
<div style="color:#9ca3af;">PM2.5</div>
<div>{latest['pm2_5']} µg/m³</div>

<div style="color:#9ca3af;margin-top:10px;">PM10</div>
<div>{latest['pm10']} µg/m³</div>
</div>

</div>
""", unsafe_allow_html=True)


# ---------------- AQI SCALE ---------------- #

st.subheader("Air Quality Scale")

aqi_pos = get_position(aqi)

st.markdown(f"""
<div style="margin-top:15px;">

<div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:6px;">
<span>Good</span>
<span>Moderate</span>
<span>Unhealthy(S)</span>
<span>Unhealthy</span>
<span>Very Unhealthy</span>
<span>Hazardous</span>
</div>

<div style="position:relative; height:16px; border-radius:10px; overflow:hidden;">

<div style="position:absolute; width:16.66%; height:100%; background:#2ecc71;"></div>
<div style="position:absolute; left:16.66%; width:16.66%; height:100%; background:#f1c40f;"></div>
<div style="position:absolute; left:33.33%; width:16.66%; height:100%; background:#e67e22;"></div>
<div style="position:absolute; left:50%; width:16.66%; height:100%; background:#e74c3c;"></div>
<div style="position:absolute; left:66.66%; width:16.66%; height:100%; background:#8e44ad;"></div>
<div style="position:absolute; left:83.33%; width:16.66%; height:100%; background:#7f1d1d;"></div>

<div style="
position:absolute;
left:{aqi_pos:.2f}%;
top:-6px;
width:18px;
height:18px;
border-radius:50%;
background:white;
border:3px solid black;
transform:translateX(-50%);
box-shadow:0 0 6px rgba(0,0,0,0.6);
z-index:10;
"></div>

</div>

<div style="position:relative; height:18px; font-size:12px; color:#9ca3af; margin-top:6px;">

<span style="position:absolute; left:0%;">0</span>
<span style="position:absolute; left:16.66%; transform:translateX(-50%);">50</span>
<span style="position:absolute; left:33.33%; transform:translateX(-50%);">100</span>
<span style="position:absolute; left:50%; transform:translateX(-50%);">150</span>
<span style="position:absolute; left:66.66%; transform:translateX(-50%);">200</span>
<span style="position:absolute; left:83.33%; transform:translateX(-50%);">300+</span>

</div>
""", unsafe_allow_html=True)


# ---------------- POLLUTANTS ---------------- #

st.subheader("Major Air Pollutants")

col1, col2 = st.columns(2)

def card(name, value, unit):
    return f"""
    <div style="background:#1f2937;padding:16px;border-radius:12px;margin-bottom:10px;">
        <div style="color:#cbd5f5;">{name}</div>
        <div style="font-size:20px;font-weight:bold;">{value} {unit}</div>
    </div>
    """

with col1:
    st.markdown(card("PM2.5", latest["pm2_5"], "µg/m³"), unsafe_allow_html=True)
    st.markdown(card("SO₂", latest["so2"], "ppb"), unsafe_allow_html=True)
    st.markdown(card("NO₂", latest["no2"], "ppb"), unsafe_allow_html=True)

with col2:
    st.markdown(card("PM10", latest["pm10"], "µg/m³"), unsafe_allow_html=True)
    st.markdown(card("CO", latest["co"], "ppb"), unsafe_allow_html=True)
    st.markdown(card("O₃", latest["o3"], "ppb"), unsafe_allow_html=True)


# ---------------- LAST 2 HOURS TABLE ---------------- #

st.subheader("Last 2 Hours Data (10 min interval)")

end_time = city_df["timestamp"].max()
start_time = end_time - timedelta(hours=2)

last_2h = city_df[
    (city_df["timestamp"] >= start_time) &
    (city_df["timestamp"] <= end_time)
].copy()

last_2h["timestamp"] = last_2h["timestamp"].dt.floor("10min")

last_2h = last_2h.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
last_2h = last_2h.tail(12)

st.dataframe(last_2h, use_container_width=True)


# ---------------- AUTO REFRESH ---------------- #

time.sleep(10)
st.rerun()