import requests
import json

def test_api():
    url = 'http://127.0.0.1:8000/predict'
    data = {
        'latitude': 32.772607,
        'longitude': -117.193877,
        'timestamp': '2025-04-15'
    }
    
    response = requests.post(url, json=data)
    print("\nTest Results:")
    print("Status Code:", response.status_code)
    
    pretty_json = json.dumps(response.json(), indent=4)
    print(pretty_json)
    
def test_upload():
    url = 'http://127.0.0.1:8000/upload'
    data = {
        'coordinates': [32.782607, -117.193877],
        'timestamp': '2025-04-15'
    }
    
    response = requests.post(url, json=data)
    print("\nTest Results:")
    print("Status Code:", response.status_code)
    
    pretty_json = json.dumps(response.json(), indent=4)
    print(pretty_json)
    
def test_upload_bulk():
    url = 'http://127.0.0.1:8000/upload_bulk'
    
    # Open file in binary mode for multipart/form-data
    files = {
        'file': ('test.csv', open('test.csv', 'rb'), 'text/csv')
    }
    
    response = requests.post(url, files=files)
    print("\nTest Results:")
    print("Status Code:", response.status_code)
    
    try:
        pretty_json = json.dumps(response.json(), indent=4)
        print(pretty_json)
    except requests.exceptions.JSONDecodeError:
        print("Error: Could not decode JSON response")
        print("Response content:", response.text)

if __name__ == '__main__':
    test_upload_bulk() 
    
