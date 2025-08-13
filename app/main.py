from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
from tensorflow.keras.losses import MeanSquaredError
import joblib
import math
from app.utils import fetch_weather_data, fetch_all_day_weather_data

# ✅ Initialize FastAPI
app = FastAPI(title="Solar Power Prediction API", description="Predict solar power using Open-Meteo weather data")

# ✅ CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔒 Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load ML Model & Scaler
try:
    model = tf.keras.models.load_model(
        "app/solarPredictionModel.h5",
        custom_objects={"mse": MeanSquaredError()}
    )
    scaler = joblib.load("app/solar_scaler.pkl")
    print("✅ Model and Scaler loaded successfully.")
except Exception as e:
    print(f"❌ Model loading error: {e}")
    raise RuntimeError(f"Model or scaler failed to load: {e}")

FEATURE_ORDER = ["Irradiance", "Temperature", "Humidity", "hr_sin", "hr_cos"]

# ✅ Request Schema
class SensorData(BaseModel):
    temperature: float
    irradiance: float
    humidity: float
    hr: float  # Hour (0–23)

# ✅ Prediction Utility
def make_prediction(irradiance, temperature, humidity, hr) -> float:
    try:
        if hr >= 18.0 or hr < 5.0:  # Nighttime → 0 power
            return 0.0

        hr_sin = math.sin(2 * math.pi * hr / 24)
        hr_cos = math.cos(2 * math.pi * hr / 24)

        input_vector = np.array([[irradiance, temperature, humidity, hr_sin, hr_cos]])
        scaled_input = scaler.transform(input_vector)
        prediction = model.predict(scaled_input)[0][0]
        return max(0.0, float(prediction))
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return 0.0

# ✅ 1. Sensor-Based Prediction
@app.post("/predict/sensor")
async def predict_from_sensor(data: SensorData):
    try:
        power = make_prediction(data.irradiance, data.temperature, data.humidity, data.hr)
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
    except Exception as e:
        print(f"❌ /predict/sensor failed: {e}")
        raise HTTPException(status_code=500, detail="Sensor prediction failed")

# ✅ 2. Current Hour Forecast
@app.get("/predict/current")
async def predict_current_hour():
    try:
        weather = fetch_weather_data()
        power = make_prediction(weather["irradiance"], weather["temperature"], weather["humidity"], weather["hr"])
        hr_sin = math.sin(2 * math.pi * weather["hr"] / 24)
        hr_cos = math.cos(2 * math.pi * weather["hr"] / 24)

        return {
            "source": "open-meteo-current-hour",
            **weather,
            "hr_sin": hr_sin,
            "hr_cos": hr_cos,
            "predicted_power": power
        }
    except Exception as e:
        print(f"❌ /predict/current failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ✅ 3. Full Day Forecast
@app.get("/predict/day")
async def predict_whole_day():
    try:
        all_hours = fetch_all_day_weather_data()
        results = []

        for hour_data in all_hours:
            power = make_prediction(hour_data["irradiance"], hour_data["temperature"], hour_data["humidity"], hour_data["hr"])
            hr_sin = math.sin(2 * math.pi * hour_data["hr"] / 24)
            hr_cos = math.cos(2 * math.pi * hour_data["hr"] / 24)

            results.append({
                **hour_data,
                "hr_sin": hr_sin,
                "hr_cos": hr_cos,
                "predicted_power": power
            })

        return {"source": "open-meteo-24-hour", "forecast": results}
    except Exception as e:
        print(f"❌ /predict/day failed: {e}")
        raise HTTPException(status_code=500, detail="Day forecast failed")

# ✅ 4. Specific Hour Forecast
@app.get("/predict/hour")
async def predict_specific_hour(hour: int = Query(..., ge=0, le=23)):
    try:
        all_hours = fetch_all_day_weather_data()
        hour_data = next((item for item in all_hours if item["hr"] == hour), None)

        if not hour_data:
            raise HTTPException(status_code=404, detail=f"No forecast found for hour {hour}")

        power = make_prediction(hour_data["irradiance"], hour_data["temperature"], hour_data["humidity"], hour_data["hr"])
        hr_sin = math.sin(2 * math.pi * hour_data["hr"] / 24)
        hr_cos = math.cos(2 * math.pi * hour_data["hr"] / 24)

        return {
            "source": f"open-meteo-hour-{hour}",
            **hour_data,
            "hr_sin": hr_sin,
            "hr_cos": hr_cos,
            "predicted_power": power
        }
    except Exception as e:
        print(f"❌ /predict/hour failed: {e}")
        raise HTTPException(status_code=500, detail="Hour forecast failed")
