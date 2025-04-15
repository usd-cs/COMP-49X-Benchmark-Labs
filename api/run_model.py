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
model_path = 'Notebook/model.knn'

#for troubleshooting
print("Model Path:", model_path) 
print("Absolute Model Path:", os.path.abspath(model_path))
if not os.path.exists(model_path):
    print("Model file does not exist at the specified path.")
model = joblib.load(model_path)  # Adjust the path as necessary

METEOS_API_URL = "https://api.open-meteo.com/v1/forecast"

# Fetch historical weather data from the NASA API, returns hourly data
def get_nasa_data(lat, lon, start_date, end_date):
    url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
    
    print(f"Getting NASA data for {lat}, {lon} from {start_date} to {end_date}")
    
    param_list = ['T2M', 'RH2M', 'T2MDEW', 'PRECTOTCORR', 'TSOIL1', 'T2MWET']
    parameters = {
        "parameters": ",".join(param_list),
        "community": "AG",
        "latitude": lat,
        "longitude": lon,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }
    
    curr_data = {}

    response = requests.get(url, params=parameters)
    data = response.json()
    try:
        for param in param_list:
            curr_data[param] = data['properties']['parameter'][param]
        return curr_data
    except:
        print(f"Error getting data")
        return None

# Save hourly NASA data into a dataframe, return dataframe
def save_nasa_data(weather_data):
    dataframe = pd.DataFrame(columns=['Datetime', 'Temperature', 'Humidity', 'Precipitation', 'Dew/Frost Point', 'Wet Bulb Temperature', 'Soil Temperature'])
    dates = list(weather_data['T2M'].keys())
    temp_values = list(weather_data['T2M'].values())
    humidity_values = list(weather_data['RH2M'].values())
    dew_frost_values = list(weather_data['T2MDEW'].values())
    precipitation_values = list(weather_data['PRECTOTCORR'].values())
    soil_temperature_values = list(weather_data['TSOIL1'].values())
    wet_bulb_values = list(weather_data['T2MWET'].values())
    curr_df = pd.DataFrame({
        'Datetime': dates,
        'Temperature': temp_values,
        'Humidity': humidity_values,
        'Precipitation': precipitation_values,
        'Dew/Frost Point': dew_frost_values,
        'Wet Bulb Temperature': wet_bulb_values,
        'Soil Temperature': soil_temperature_values
    })
        
    dataframe = pd.concat([dataframe, curr_df], ignore_index=True)
    
    return dataframe

# Fetch forecasted weather data from Meteos API, returns hourly data
def get_meteos_data(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    
    param_list = ['temperature_2m', 'relative_humidity_2m', 'dew_point_2m', 'precipitation', 'soil_temperature_6cm', 'wet_bulb_temperature_2m']
    
    parameters = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(param_list),
        "past_days": 7,
        "forecast_days": 14
    }
    
    curr_data = {}

    response = requests.get(url, params=parameters)
    data = response.json()
    try:
        for param in param_list:
            curr_data[param] = data['hourly'][param]
                    
        # Convert datetime strings to proper format
        formatted_datetimes = []
        for dt_str in data['hourly']['time']:
            converted_date = (datetime.strptime(dt_str, "%Y-%m-%dT%H:%M")).strftime("%Y%m%d%H")
            formatted_datetimes.append(converted_date)
        
        curr_data['Datetime'] = formatted_datetimes
                
        return curr_data
    except:
        print(f"Error getting data")
        return None

# Save hourly forecasted Meteos data into a dataframe, return dataframe
def save_meteos_data(weather_data):
    dataframe = pd.DataFrame(columns=['Datetime', 'Temperature', 'Humidity', 'Precipitation', 'Dew/Frost Point', 'Wet Bulb Temperature', 'Soil Temperature'])
    dates = list(weather_data['Datetime'])
    temp_values = list(weather_data['temperature_2m'])
    humidity_values = list(weather_data['relative_humidity_2m'])
    dew_frost_values = list(weather_data['dew_point_2m'])
    precipitation_values = list(weather_data['precipitation'])
    soil_temperature_values = list(weather_data['soil_temperature_6cm'])
    wet_bulb_values = list(weather_data['wet_bulb_temperature_2m'])
    curr_df = pd.DataFrame({
        'Datetime': dates,
        'Temperature': temp_values,
        'Humidity': humidity_values,
        'Precipitation': precipitation_values,
        'Dew/Frost Point': dew_frost_values,
        'Wet Bulb Temperature': wet_bulb_values,
        'Soil Temperature': soil_temperature_values
    })
        
    dataframe = pd.concat([dataframe, curr_df], ignore_index=True)
    
    return dataframe

def calculate_aggregates(weather_subset, var_name, window_name, start_day, end_day):
    # Filter data for given time window
    window_data = weather_subset[(weather_subset['RelativeDay'] >= start_day) & (weather_subset['RelativeDay'] <= end_day)]
    
    # Calculate aggregate and return as a series
    result = pd.Series({
        f"{var_name}_{window_name}_mean": window_data[var_name].mean(),
        f"{var_name}_{window_name}_min": window_data[var_name].min(),
        f"{var_name}_{window_name}_max": window_data[var_name].max(),
        f"{var_name}_{window_name}_median": window_data[var_name].median()
    })
    
    return result

# Process NASA dataframe into aggregate window features, return new dataframe
def process_data(weather_df, timestamp):
    
    # convert datetime to same format as observations_df
    weather_df['Datetime'] = pd.to_datetime(weather_df['Datetime'], format='%Y%m%d%H')
    weather_df['Date'] = weather_df['Datetime'].dt.date

    # Calculate difference between observation date and weather date
    def get_relative_day(row):
        obs_date = pd.to_datetime(timestamp)
        this_date = pd.to_datetime(row['Date'])
        difference = (this_date - obs_date).days
        return difference
    
    # Apply the function to get relative day
    weather_df['RelativeDay'] = weather_df.apply(get_relative_day, axis=1)

    # Variables to calculate aggregations for
    weather_vars = ['Temperature', 'Humidity', 'Precipitation', 'Dew/Frost Point', 'Wet Bulb Temperature', 'Soil Temperature']

    # Time windows to aggregate over (days before and after the observation day)
    time_windows = {
        'day_of': (0, 0),
        'day_before_after': (-1, 0),
        'two_days': (-2, 0),
        'three_days': (-3, 0),
        'one_week': (-7, 0),
        'two_week': (-14, 0)
    }
    
    # Dictionary to store aggregated values
    features = {}
    
    # Iterate over all weather data variables
    for var in weather_vars:
        # iterate over all items in time_windows
        for window_name, (start_day, end_day) in time_windows.items():
            # Filter data for given time window
            window_data = weather_df[(weather_df['RelativeDay'] >= start_day) & (weather_df['RelativeDay'] <= end_day)]
            
            # Calculate aggregates
            features[f"{var}_{window_name}_mean"] = window_data[var].mean()
            features[f"{var}_{window_name}_min"] = window_data[var].min()
            features[f"{var}_{window_name}_max"] = window_data[var].max()
            features[f"{var}_{window_name}_median"] = window_data[var].median()

    # Create DataFrame from results
    features_df = pd.DataFrame([features])
    
    # Add day of year feature based on timestamp
    day_of_year = pd.to_datetime(timestamp).dayofyear
    features['day_of_year'] = day_of_year
    
    # Update the features DataFrame with the new feature
    features_df = pd.DataFrame([features])
    
    return features_df

# Take location and time, return prediction and confidence
@app.route('/predict', methods=['POST'])
def predict():
    
    # Request data from client
    data = request.get_json()
    print("Received data:", data)
    lat = data['latitude']
    lon = data['longitude']
    timestamp = data['timestamp']

    # Get NASA data for the past 3 weeks - 1 week ago
    end_date = datetime.strptime(timestamp, "%Y-%m-%d")
    start_date = end_date - timedelta(days=21)
    end_date = end_date - timedelta(days=7)

    nasa_data = get_nasa_data(lat, lon, start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
    nasa_df = save_nasa_data(nasa_data)
    
    # Get Meteos data for the next two weeks
    meteos_data = get_meteos_data(lat, lon)
    meteos_df = save_meteos_data(meteos_data)
            
    # Concatenate the dataframes
    combined_df = pd.concat([nasa_df, meteos_df])
    
    # When Datetime is the same, keep the meteos_df row by dropping duplicates
    # and keeping the last occurrence (meteos_df rows come after nasa_df rows in the concatenated dataframe)
    combined_df = combined_df.drop_duplicates(subset='Datetime', keep='last')
    
    # Sort by Datetime to maintain chronological order
    combined_df = combined_df.sort_values('Datetime')

    # Process data and make predictions for the next 7 days at 12-hour intervals
    results = []
    
    # Convert timestamp to datetime object
    base_datetime = datetime.strptime(timestamp, "%Y-%m-%d")
    
    #  Predict for 7 days, 12-hour intervals (14 steps)
    for step in range(15): 
        
        # Convert step to hours and add to current time
        hours_ahead = step * 12
        curr_time = base_datetime + timedelta(hours=hours_ahead)
        
        # Get aggregate features at this time
        features_df = process_data(combined_df, curr_time)
        
        # Predict, get response and confidence of True (PMI)
        prediction = model.predict(features_df)[0]
        confidence = model.predict_proba(features_df)[0][1]
        
        # Save results
        results.append({
            'step': step,
            'timestamp': curr_time.strftime("%Y-%m-%d %H:%M:%S"),
            'prediction': bool(prediction),
            'confidence': float(confidence)
        })
    
    # Return to API query
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)

