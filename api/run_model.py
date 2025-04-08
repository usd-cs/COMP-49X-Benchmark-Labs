import os
print("Current Working Directory:", os.getcwd()) #for troubleshooting

from flask import Flask, request, jsonify
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import joblib

app = Flask(__name__)

# Load your trained model
model_path = 'Notebook/model.randomforest'

#for troubleshooting
print("Model Path:", model_path) 
print("Absolute Model Path:", os.path.abspath(model_path))
if not os.path.exists(model_path):
    print("Model file does not exist at the specified path.")
model = joblib.load(model_path)  # Adjust the path as necessary

NASA_API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
METEOS_API_URL = "https://api.open-meteo.com/v1/forecast"

def get_nasa_data(lat, lon, start_date, end_date):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }
    response = requests.get(NASA_API_URL, params=params)
    data = response.json()
    return data

def get_meteos_data(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,dew_point_2m",
        "forecast_days": 16
    }
    response = requests.get(METEOS_API_URL, params=params)
    data = response.json()
    return data

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    print("Received data:", data)
    lat = data['latitude']
    lon = data['longitude']
    timestamp = data['timestamp']

    # Get NASA data for the past two weeks
    end_date = datetime.strptime(timestamp, "%Y-%m-%d")
    start_date = end_date - timedelta(days=14)
    nasa_data = get_nasa_data(lat, lon, start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))

    # Get Meteos data for the next 14 days
    meteos_data = get_meteos_data(lat, lon)

    # Combine data and make predictions
    predictions = []
    for i in range(0, 14*4, 6):
        # Combine NASA and Meteos data
        combined_data = combine_data(nasa_data, meteos_data, i)
        prediction = model.predict(combined_data)
        predictions.append({
            "timestamp": (end_date + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S"),
            "confidence_interval": prediction
        })

    print("Predictions:", predictions)
    return jsonify(predictions)

def combine_data(nasa_data, meteos_data, hours_ahead):
    # Combine the data from NASA and Meteos
    # This function needs to be implemented based on your model's requirements
    pass

if __name__ == '__main__':
    app.run(debug=True)

    # Test the API
    url = 'http://127.0.0.1:5000/predict'
    data = {
        'latitude': 51.505,
        'longitude': -0.09,
        'timestamp': '2025-04-06'
    }
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

