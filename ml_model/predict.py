import joblib
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "lipid_model.pkl")

# Load model once globally
_model = joblib.load(MODEL_PATH)

def predict_risk(ldl, hdl, tg, total_chol):
    try:
        features = np.array([[ldl, hdl, tg, total_chol]], dtype=float)
        prediction = _model.predict(features)
        return prediction[0]  # Return label string (Low/Medium/High/Very High)
    except Exception as e:
        print("Prediction error:", e)
        return "Error"
