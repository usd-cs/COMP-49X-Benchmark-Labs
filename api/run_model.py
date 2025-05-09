import os
from flask import Flask, request, jsonify
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import joblib
import csv
import pymongo

app = Flask(__name__)

# Load trained model
model_path = os.environ.get('MODEL_PATH', 'Notebook/model.knn')
model = joblib.load(model_path)
                    
# I know this shouldn't be hardcoded, but DB is just for test purposes at the moment
MONGODB_URI = os.environ.get('MONGODB_URI', "mongodb+srv://benchmark:PMIUpload@pmi-upload.uvwlyon.mongodb.net/?retryWrites=true&w=majority&appName=PMI-Upload")

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

def find_category(prediction, confidence):
    # as of now these are arbitrary thresholds, need testing to determine best values
    if prediction:
        if confidence > 0.90:
            return "Extremely High"
        elif confidence > 0.75:
            return "Very High"
        elif confidence > 0.55:
            return "High"
        else:
            return "Medium"
    else:
        if confidence > 0.90:
            return "Extremely Low"
        elif confidence > 0.75:
            return "Very Low"
        elif confidence > 0.55:
            return "Low"
        else:
            return "Medium"
        
        

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
        # Convert DataFrame to numpy array to drop feature names
        features_array = features_df.values
        # prediction is array of classes [False] or [True]
        prediction = model.predict(features_array)[0]
        # returns list of probabilities for each class [x,y] where x is probability of False and y is probability of True
        confidences = model.predict_proba(features_array)[0]
        if prediction:
            confidence = confidences[1]
        else:
            confidence = confidences[0]

        # Save results
        results.append({
            'step': step,
            'timestamp': curr_time.strftime("%Y-%m-%d %H:%M:%S"),
            'prediction': bool(prediction),
            'confidence': float(confidence),
            'category': find_category(prediction, confidence)
        })
    
    # Return to API query
    return jsonify(results)

# Allow users to upload their powdery mildew observations, use for training
@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    
    try:
        coords = data['coordinates']
        timestamp = data['timestamp']
        
        # Create document for MongoDB
        observation = {
            "coordinates": coords,
            "timestamp": timestamp
        }
        
        # Connect to MongoDB and upload the data
        client = pymongo.MongoClient(MONGODB_URI)
        db = client.pmi_data
        collection = db.observations
        
        # Insert the observation
        collection.insert_one(observation)
        client.close()
        
        return jsonify({"message": "Data received and uploaded to MongoDB"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Allow users to upload bulk observations as CSV
@app.route('/upload_bulk', methods=['POST'])
def upload_bulk():
        
    file = request.files['file']
        
    try:
                
        # Read the CSV file
        csv_data = []
        csv_file = file.read().decode('utf-8').splitlines()
        csv_reader = csv.reader(csv_file)
        
        # Skip header if it exists
        header = next(csv_reader, None)
        
        # Process each row
        for row in csv_reader:
            lat = row[0]
            lon = row[1]
            timestamp = row[2]
                
            # Add to our data collection
            csv_data.append({
                "coordinates": [float(lat), float(lon)],
                "timestamp": timestamp
            })
                    
        # Connect to MongoDB and upload the data
        client = pymongo.MongoClient(MONGODB_URI)
        db = client.pmi_data
        collection = db.observations
        
        # Insert the processed data
        if csv_data:
            collection.insert_many(csv_data)
            client.close()
        
        return jsonify({"message": "Data received and uploaded to MongoDB"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
