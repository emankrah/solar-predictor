from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
from tensorflow.keras.losses import MeanSquaredError
import joblib
import math
from app.utils import fetch_weather_data, fetch_all_day_weather_data

app = FastAPI()

# Load model and scaler
try:
    model = tf.keras.models.load_model(
    "app/solarPredictionModel.h5",
    custom_objects={'mse': MeanSquaredError()}
)
    scaler = joblib.load("app/solar_scaler.pkl")
    print("Model and Scaler loaded.")
except Exception as e:
    raise RuntimeError(f"Model or scaler failed to load: {e}")

# Define feature order
FEATURE_ORDER = [ "Irradiance","Temperature", "Humidity", "hr_sin", "hr_cos"]

# Pydantic model for sensor input
class SensorData(BaseModel):
    temperature: float
    irradiance: float
    humidity: float
    hr: float  # Plain hour (0–23)


# Utility to convert hr → hr_sin/hr_cos and predict
def make_prediction( irradiance,temperature, humidity, hr) -> float:
    if hr >= 18.0 or hr < 5.0:
        return 0.0

    hr_sin = math.sin(2 * math.pi * hr / 24)
    hr_cos = math.cos(2 * math.pi * hr / 24)

    input_vector = np.array([[ irradiance,temperature, humidity, hr_sin, hr_cos]])
    scaled_input = scaler.transform(input_vector)

    prediction = model.predict(scaled_input)[0][0]
    return max(0.0, float(prediction))


# 1. Sensor-based Prediction
@app.post("/predict/sensor")
async def predict_from_sensor(data: SensorData):
    power = make_prediction( data.irradiance,data.temperature, data.humidity, data.hr)
    hr_sin = math.sin(2 * math.pi * data.hr / 24)
    hr_cos = math.cos(2 * math.pi * data.hr / 24)

    return {
        "source": "sensor",
        "temperature": data.temperature,
        "irradiance": data.irradiance,
        "humidity": data.humidity,
        "hr": data.hr,
        "hr_sin": hr_sin,
        "hr_cos": hr_cos,
        "predicted_power": power
    }


# 2. Current Hour Forecast
@app.get("/predict/current")
async def predict_current_hour():
    try:
        weather = fetch_weather_data()
        power = make_prediction( weather["irradiance"],weather["temperature"], weather["humidity"], weather["hr"])
        hr_sin = math.sin(2 * math.pi * weather["hr"] / 24)
        hr_cos = math.cos(2 * math.pi * weather["hr"] / 24)

        return {
            "source": "weather-api-current-hour",
            **weather,
            "hr_sin": hr_sin,
            "hr_cos": hr_cos,
            "predicted_power": power
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 3. Full Day Forecast
@app.get("/predict/day")
async def predict_whole_day():
    try:
        all_hours = fetch_all_day_weather_data()
        results = []

        for hour_data in all_hours:
            power = make_prediction( hour_data["irradiance"],hour_data["temperature"], hour_data["humidity"], hour_data["hr"])
            hr_sin = math.sin(2 * math.pi * hour_data["hr"] / 24)
            hr_cos = math.cos(2 * math.pi * hour_data["hr"] / 24)

            results.append({
                **hour_data,
                "hr_sin": hr_sin,
                "hr_cos": hr_cos,
                "predicted_power": power
            })

        return {
            "source": "weather-api-24-hour",
            "forecast": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 4. Specific Hour Forecast
@app.get("/predict/hour")
async def predict_specific_hour(hour: int = Query(..., ge=0, le=23)):
    try:
        all_hours = fetch_all_day_weather_data()
        hour_data = next((item for item in all_hours if item["hr"] == hour), None)

        if not hour_data:
            raise HTTPException(status_code=404, detail=f"No forecast found for hour {hour}")

        power = make_prediction( hour_data["irradiance"],hour_data["temperature"], hour_data["humidity"], hour_data["hr"])
        hr_sin = math.sin(2 * math.pi * hour_data["hr"] / 24)
        hr_cos = math.cos(2 * math.pi * hour_data["hr"] / 24)

        return {
            "source": f"weather-api-hour-{hour}",
            **hour_data,
            "hr_sin": hr_sin,
            "hr_cos": hr_cos,
            "predicted_power": power
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
