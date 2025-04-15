import requests
import json

def test_api():
    url = 'http://127.0.0.1:5000/predict'
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


if __name__ == '__main__':
    test_api() 