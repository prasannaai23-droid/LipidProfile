import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset (update path if different)
df = pd.read_csv("lipid_dataset_5000.csv")

# Select features for training
feature_cols = [
    "Age", "LDL", "HDL", "Triglycerides",
    "Glucose", "BMI", "Smoking", "FamilyHistory"
]

X = df[feature_cols]
y = df["Risk"]

# Encode target labels
risk_encoder = LabelEncoder()
y = risk_encoder.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model training
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Save model + label encoder
joblib.dump(model, "risk_model.pkl")
joblib.dump(risk_encoder, "risk_encoder.pkl")

# Evaluate
accuracy = model.score(X_test, y_test)
print(f"✅ Model Training Complete - Accuracy: {accuracy * 100:.2f}%")
