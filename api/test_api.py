import requests

def test_api():
    url = 'http://127.0.0.1:5000/predict'
    data = {
        'latitude': 51.505,
        'longitude': -0.09,
        'timestamp': '2025-04-09'
    }
    response = requests.post(url, json=data)
    print("\nTest Results:")
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

if __name__ == '__main__':
    test_api() 