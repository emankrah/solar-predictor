import requests
from datetime import datetime
from typing import List, Dict

API_KEY = "c14aedc7193d406e919163328252406"
LAT = "6.670678731388893"
LON = "-1.560145615345082"

def fetch_weather_data():
    url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={LAT},{LON}&days=1&aqi=no&alerts=no"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Access hourly forecast data
    hourly_forecast = data["forecast"]["forecastday"][0]["hour"]

    now = datetime.now()  # Use naive datetime for local time
    selected_forecast = None

    for item in hourly_forecast:
        forecast_time = datetime.strptime(item["time"], "%Y-%m-%d %H:%M")
        if forecast_time.hour == now.hour:
            selected_forecast = item
            break

    if not selected_forecast:
        selected_forecast = hourly_forecast[0]

    temperature = selected_forecast["temp_c"]
    humidity = selected_forecast["humidity"]
    dt_txt = selected_forecast["time"]
    hr = int(dt_txt.split()[1].split(":")[0])

    irradiance = selected_forecast.get("solar_rad", 0.0)  # ✔️ Use .get() safely

    return {
        "temperature": temperature,
        "humidity": humidity,
        "irradiance": irradiance,
        "hr": hr,
        "datetime": dt_txt
    }


def fetch_all_day_weather_data() -> List[Dict]:
    """
    Fetches hourly weather forecast data for the current day from WeatherAPI.com.
    Uses 'short_rad' (solar irradiance) directly.
    Returns a list of dictionaries with temperature, humidity, irradiance, hour, and datetime.
    """
    url = f"https://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={LAT},{LON}&days=1&aqi=no&alerts=no"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    hourly_forecast = data["forecast"]["forecastday"][0]["hour"]
    all_day_data = []

    for item in hourly_forecast:
        dt_txt = item["time"]
        hr = int(dt_txt.split()[1].split(":")[0])
        temperature = item.get("temp_c", 0.0)
        humidity = item.get("humidity", 0)
        irradiance = item.get("short_rad", 0.0)  # ✅ Directly use 'short_rad' only

        all_day_data.append({
            "temperature": temperature,
            "humidity": humidity,
            "irradiance": irradiance,
            "hr": hr,
            "datetime": dt_txt
        })

    return all_day_data


fetch_weather_data()