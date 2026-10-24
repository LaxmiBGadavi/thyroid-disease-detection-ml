import pandas as pd
import joblib
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load model and encoder
model = joblib.load("thyroid_model.pkl")
le = joblib.load("label_encoder.pkl")

# Load dataset
df = pd.read_csv(r"C:\Thyroid_001\backend_001\thyroid_balanced_6000_clean.xls")

# Prepare features and target
X = df.drop("target", axis=1)
y_true = df["target"].values

# Make predictions on entire dataset
y_pred_encoded = model.predict(X)
y_pred = le.inverse_transform(y_pred_encoded)

# Calculate accuracy
accuracy = accuracy_score(y_true, y_pred)

print("="*60)
print("THYROID MODEL ACCURACY REPORT")
print("="*60)
print(f"Dataset Size: {len(df)} samples")
print(f"Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_true, y_pred))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_true, y_pred)
print(cm)

# Show some sample predictions
print("\nSample Predictions (first 10):")
for i in range(min(10, len(df))):
    actual = y_true[i]
    predicted = y_pred[i]
    status = "CORRECT" if actual == predicted else "WRONG"
    print(f"{status} - Actual: {actual:<12} | Predicted: {predicted:<12}")

print("\n" + "="*60)