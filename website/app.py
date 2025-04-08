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

if __name__ == '__main__':
    app.run(debug=True, port=8000)
