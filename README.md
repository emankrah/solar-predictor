# Solar Energy Predictor API

This project provides an API for predicting the energy output of a solar panel. The model takes in the following features:

- **Irradiance**  
- **Temperature**  
- **Hour** (processed into sine and cosine form)  
- **Humidity**  

It predicts the energy (power) that the solar panel is expected to produce for a given hour.

---

## 🌐 Virtual Environment Setup

To set up and activate a Python virtual environment:

```bash
# Create the virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# OR on Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## ⚠️ Key Challenges Faced

- The model is trained on **synthetic (fictitious)** data. Real solar panel output was not available.
- Power values were generated using a physics-based formula with a **20W** solar panel rating under standard conditions.
  
- ## **Formula Used for Power Generation**:

  $$
  P_{actual} = P_{rated} \times \left( \frac{G_{actual}}{G_{STC}} \right) \times \left[ 1 + \alpha_P \times (T_{cell,actual} - T_{cell,STC}) \right] \times PR
  $$

  - **$P_{rated}$** = Rated power of the solar panel (**20W**)  
  - **$G_{actual}$** = Global Horizontal Irradiance (from weather data)  
  - **$G_{STC}$** = Irradiance at Standard Test Conditions (**1000 W/m²**)  
  - **$\alpha_P$** = Temperature coefficient of power  
  - **$T_{cell,actual}$** = Actual solar cell temperature  
  - **$T_{cell,STC}$** = Standard temperature (**25°C**)  
  - **$PR$** = Performance Ratio (accounts for system losses, typically between 0.65 and 0.85)

- The model was trained on **10 years of weather data**, but it had trouble learning the relationship between time (hour of day) and power output.

- To resolve this, **hour** was transformed into two features:  
  - `hr_sin = sin(2π × hr / 24)`  
  - `hr_cos = cos(2π × hr / 24)`

  These allow the model to better understand time as a **cyclical feature** (e.g., 23:00 is close to 0:00). The API performs this conversion automatically — users should simply provide the hour as an integer from **0 to 23**.

---




## ✅ Summary

- This API uses weather inputs and hour of day to estimate solar power output from a **20W panel**.
- It is ideal for **prototyping**, **simulation**, or **educational purposes**, as it is based on a modeled dataset.
- Hour handling is **cyclical**, improving model accuracy during transitions between night and day.
- The panel’s power behavior is modeled after realistic solar physics using temperature and irradiance dynamics.

---

> 💡 *This project can be expanded further with real sensor data to fine-tune accuracy and enable smarter energy management systems.*
