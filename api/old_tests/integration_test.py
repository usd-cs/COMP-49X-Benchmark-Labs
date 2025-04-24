import pytest
import requests
import json



def test_integration():
    # data is from clicking center of the map on the website
    data = {'latitude': 39.842286020743394, 'longitude': -98.61328125, 'timestamp': '2025-04-11'}
    response = requests.post('http://127.0.0.1:5000/predict', json=data)
    
    # check response is 200 OK response
    assert response.status_code == 200
    # check response is the correct response that it should be
    correct_response =  json.load(open('api/correct_response.json'))
    assert response.json() == correct_response
