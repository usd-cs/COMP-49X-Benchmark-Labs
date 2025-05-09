import requests
import json

def test_upload():
    url = 'http://127.0.0.1:5000/upload'
    data = {
        'coordinates': [32.782607, -117.193877],
        'timestamp': '2025-04-15'
    }

    response = requests.post(url, json=data)

    assert response.status_code == 200
    assert response.json().get('message') == 'Data received and uploaded to MongoDB'

def test_upload_bulk():
    url = 'http://127.0.0.1:5000/upload_bulk'
    filename = "api/test.csv"
    data = {
        'file': ('api/test.csv', open(filename, 'rb'), 'text/csv'),
    }
    response = requests.post(url, files=data)
    assert response.status_code == 200
    assert response.json().get('message') == "Data received and uploaded to MongoDB"

def test_predict():
    url = 'http://127.0.0.1:5000/predict'
    data = {'latitude': 33.46810795527896, 'longitude': -102.65625000000001, 
            'timestamp': '2025-05-09'
    }
    response = requests.post(url, json=data)
    assert response.status_code == 200
    assert 'category' in response.json()[0]
    assert 'confidence' in response.json()[0]
    assert 'prediction' in response.json()[0]
    assert 'step' in response.json()[0]
    assert 'timestamp' in response.json()[0]

def test_predict_values():
    url = 'http://127.0.0.1:5000/predict'
    data = {'latitude': 33.46810795527896, 'longitude': -102.65625000000001, 
            'timestamp': '2025-05-09'
    }
    # tests for correct values from predict
    response = requests.post(url, json=data)
    assert response.status_code == 200
    assert response.json()[0]['category'] == 'Low'
    assert response.json()[0]['confidence'] == 0.6
    assert response.json()[0]['prediction'] == False
    assert response.json()[0]['step'] == 0
    assert response.json()[0]['timestamp'] == '2025-05-09 00:00:00'

