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

