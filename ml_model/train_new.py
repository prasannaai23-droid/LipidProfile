import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# ✅ Path to CSV
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "lipid_dataset.csv")

# ✅ Load dataset
df = pd.read_csv(DATA_PATH)

# ✅ Select correct features
feature_columns = ["TC", "LDL", "HDL", "TG"]
X = df[feature_columns]
y = df["risk_level"]

# ✅ Split & train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# ✅ Save model inside ml_model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "lipid_model.pkl")
joblib.dump(model, MODEL_PATH)

print("\n✅ Model trained and saved successfully!")
print("📌 Location:", MODEL_PATH)
