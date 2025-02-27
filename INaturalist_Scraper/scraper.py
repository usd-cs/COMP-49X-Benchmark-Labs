import requests
import json
import os
import time  # Add time module for sleep functionality

def get_true_observations():
    
    url = 'https://api.inaturalist.org/v1/observations'
    params = {
        'taxon_id': 408176, # ID for "Apple Powdery Mildew"
        'order_by': 'votes',
        'quality_grade': 'research',
        'photos': 'true',
        'page': '',
        'per_page': 200 # total number of research verified observations
    }
    
    try:
        
        # Get API and parse data
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Parse data, save values we want
        processed_data = []
        for observation in data['results']:
            processed_observation = {
                'id': observation['id'], # unique ID for observation
                'date': { # detailed date
                    'day': observation['observed_on_details']['day'],
                    'month': observation['observed_on_details']['month'],
                    'year': observation['observed_on_details']['year']
                },
                'date_string': observation['time_observed_at'], # timestamp date
                'coordinates': observation['geojson']['coordinates'] # coordinates in list
            }
            processed_data.append(processed_observation)

        # Save parsed data to file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, 'Data/true_observations.json'), 'w') as f:
            json.dump(processed_data, f, indent=2)
        
        print('Data saved to true_observations.json')
        
        return processed_data

    except Exception as e:
        print(f"Error in get_true_observations: {e}")
        return []
        
def get_false_observations(true_observations):
    
    url = 'https://api.inaturalist.org/v1/observations'
    params = {
        'taxon_id': 469472, # ID for "Apple"
        
        # Coordinate bounding box to search within
        'swlat': None, 
        'swlng': None,
        'nelat': None,
        'nelng': None,
        
        'order_by': 'votes',
        'quality_grade': 'research',
        'photos': 'true',
        'page': '',
        'per_page': 200 # limit of observations per request
    }
    
    processed_data = []
    
    # Loop through true observations
    for i, observation in enumerate(true_observations):
        
        try:
            # Set bounding box (10 miles radius of true observation)
            params['swlat'] = observation['coordinates'][1] - 0.145
            params['swlng'] = observation['coordinates'][0] - 0.226
            params['nelat'] = observation['coordinates'][1] + 0.145
            params['nelng'] = observation['coordinates'][0] + 0.226
            
            print("Processing true observation", i)
            
            # Get API and parse data
            response = requests.get(url, params=params)
                            
            # Parse data, save values we want
            data = response.json()
            
            for observation in data['results']:
                processed_observation = {
                    'id': observation['id'], # unique ID for observation
                    'date': { # detailed date
                        'day': observation['observed_on_details']['day'],
                        'month': observation['observed_on_details']['month'],
                        'year': observation['observed_on_details']['year']
                    },
                    'date_string': observation['time_observed_at'], # timestamp date
                    'coordinates': observation['geojson']['coordinates'] # coordinates in list
                }
                
                # Only add data not already in processed_data
                if not any(existing_obs.get('id') == processed_observation['id'] for existing_obs in processed_data):
                    processed_data.append(processed_observation)
            
            print(f"Successfully processed false observations")
            
            # delay to avoid rate limi
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5) # wait longer before next req
        
        
    # Save parsed data to file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, 'Data/false_observations.json'), 'w') as f:
        json.dump(processed_data, f, indent=2)
    
    print('Data saved to false_observations.json')

true_observations = get_true_observations()
if true_observations:
    get_false_observations(true_observations)