# 🍎 COMP-49X Benchmark Labs: Predicting Powdery Mildew

## 🧠 Project Description

This project predicts outbreaks of *Powdery Mildew* in apple orchards using machine learning models trained on weather and disease data. Our team developed an API and simple frontend demo to forecast mildew pressure at specific locations and times. The ultimate goal is to help apple growers reduce pesticide use, prevent crop loss, and support more sustainable farming practices.

This repository contains:
- Data engineering pipelines
- Weather feature extraction scripts
- Model training notebooks (Scikit-learn & TensorFlow Decision Forests)
- A Flask API for predictions
- A basic frontend for user input

---

## ⚙️ Software Dependencies

### 🐍 Python Packages
Install these via pip using `requirements.txt`, or manually:
- `tensorflow` (>= 2.0)
- `tensorflow-decision-forests`
- `scikit-learn`
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `flask`
- `pymongo`
- `requests`

### 🌐 External APIs (No API key required)
- **NASA POWER DAV**  
  Provides historical hourly weather data for a specified lat/lon.
  - Parameters used: `T2M`, `RH2M`, `T2MDEW`, `PRECTOTCORR`, `T2MWET`, `TSOIL1`
- **Open Meteo**  
  Used for future weather forecasts up to 2 weeks. Mirrors the parameters from NASA.

---

## 🚀 How to Run This Project

### 1. Clone the repository
```bash
git clone https://github.com/your-org/COMP-49X-Benchmark-Labs.git
cd COMP-49X-Benchmark-Labs
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set any environment variables *(optional for local use)*
```bash
export FLASK_ENV=development
export MONGO_URI="mongodb://localhost:27017"
```

### 4. Run the API
```bash
cd api
python run_model.py
```

This will launch the Flask server locally on `http://127.0.0.1:5000`.

---

## 📡 API Usage

### ➤ POST `/predict`

Returns a mildew risk prediction at a given time and location. Automatically fetches weather data from NASA and Open Meteo.

#### Request Format (JSON):
```json
{
  "latitude": 47.5,
  "longitude": -120.7,
  "timestamp": "2025-04-15"
}
```

#### Example `curl` Request:
```bash
curl -X POST http://127.0.0.1:5000/predict \
-H "Content-Type: application/json" \
-d '{"latitude": 47.5, "longitude": -120.7, "timestamp": "2025-04-15"}'
```

#### Response (JSON):
```json
{
  "PMI": 0.72,
  "risk_level": "Very High",
  "message": "Powdery mildew pressure is very high. Monitor your crop closely."
}
```

---

## 📓 Notebooks

The Jupyter Notebooks are in the `/Notebook/` folder:
- `main.ipynb`: Feature engineering, model comparison (KNN, RF, SVM, XGBoost)
- `tensorflow.ipynb`: Gradient Boosted Trees using TensorFlow Decision Forests

Run via:
```bash
cd Notebook
jupyter notebook
```

---

## 🌍 Frontend Demo

The `website/` folder contains a simple HTML/JS form to:
- Pick a location on a map
- Get mildew prediction or log a mildew report via the API

To run the website locally, first start the API server by running the file `run_model.py` in the `/api/` folder. 
Then, in a new terminal, run the flask app contained in the fle `website.py` in the `/website/` folder. Click on the url generated.

---

## 🔭 Future Work

This project is a prototype. Future contributors are encouraged to:
- Replace iNaturalist data with proprietary orchard datasets
- Incorporate image-based mildew reporting into the frontend
- Use user-submitted reports to retrain the model
- Validate predictions with ground-truth field trials

---

## 👨‍🌾 Acknowledgments

Developed by:
- Dillon Timmer  
- Claire Gallagher  
- Cameron Moran  

Mentors:  
- Carlos F. Gaitan, Benchmark Labs CEO  
- Adrian Kozameh, Software Lead  
- Dr. Saturnino Garcia, Instructor
