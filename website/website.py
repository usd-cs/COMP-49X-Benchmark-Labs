from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)


@app.route('/')

def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    print("Sending data to API:", data)
    response = requests.post('http://127.0.0.1:5000/predict', json=data)
    print("API response status code:", response.status_code)
    print("API response text:", response.text)
    return jsonify(response.json())

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    print("Forwarding upload data to API:", data)
    # Forward the request to the actual API service
    response = requests.post('http://127.0.0.1:5000/upload', json=data)
    print("API response status code:", response.status_code)
    print("API response text:", response.text)
    # Check if the response was successful and contains JSON
    try:
        return jsonify(response.json()), response.status_code
    except requests.exceptions.JSONDecodeError:
        # If the API didn't return JSON, return its text content and status code
        return response.text, response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=8000)
