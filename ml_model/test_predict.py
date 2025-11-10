# ml_model/test_predict.py
import os, joblib, numpy as np, traceback

MODEL_PATHS = [
    "ml_model/risk_rf_model.pkl",
    "ml_model/risk_model.pkl",
    "ml_model/risk_rf_model.pkl",
    "risk_rf_model.pkl",
    "ml_model/risk_rf_model.pkl"
]

def find_and_load_model():
    for p in MODEL_PATHS:
        if os.path.exists(p):
            print("Loading model from:", p)
            try:
                model = joblib.load(p)
                return model, p
            except Exception as e:
                print("Failed to load model at", p, ":", e)
    raise FileNotFoundError("No model file found in known locations: " + ", ".join(MODEL_PATHS))

def main():
    try:
        model, path = find_and_load_model()
        # Dummy sample in the expected feature order (adjust if your model uses different features)
        # Example features: [age, gender_enc, bmi, blood_glucose, smoking, alcohol_enc, hypertension, family_history, TC, LDL, HDL, TG]
        sample = np.array([[45, 0, 28.5, 110.0, 0, 1, 0, 0, 240.0, 170.0, 40.0, 220.0]])
        print("Sample shape:", sample.shape)
        preds = model.predict(sample)
        print("Prediction output (raw):", preds)
        if hasattr(model, "predict_proba"):
            print("Probabilities:", model.predict_proba(sample))
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    main()
