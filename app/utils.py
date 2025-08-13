import os
from dotenv import load_dotenv
import requests
from datetime import datetime
from typing import List, Dict

# Load environment variables
load_dotenv()
LAT = float(os.getenv("LAT", 6.6707))
LON = float(os.getenv("LON", -1.5601))

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_all_day_weather_data() -> List[Dict]:
    """Fetch full day hourly forecast and convert to a structured list."""
    params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": "temperature_2m,shortwave_radiation,relative_humidity_2m",
        "forecast_days": 1
    }
    response = requests.get(OPEN_METEO_URL, params=params)
    response.raise_for_status()
    data = response.json()

    times = data["hourly"]["time"]
    temps = data["hourly"]["temperature_2m"]
    radiation = data["hourly"]["shortwave_radiation"]
    humidity = data["hourly"]["relative_humidity_2m"]

    hourly_data = []
    for i, t in enumerate(times):
        dt = datetime.fromisoformat(t)
        hourly_data.append({
            "datetime": t,
            "temperature": float(temps[i]),
            "irradiance": float(radiation[i]),
            "humidity": float(humidity[i]),
            "hr": dt.hour
        })

    return hourly_data


def fetch_weather_data() -> Dict:
    """Return current hour weather data."""
    all_data = fetch_all_day_weather_data()
    current_hour = datetime.now().hour
    return next((h for h in all_data if h["hr"] == current_hour), all_data[0])
