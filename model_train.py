import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib
import os

print("Loading dataset...")

# Show where Python is running from
print("Current Working Directory:", os.getcwd())

df = pd.read_csv(r"C:\Thyroid_001\backend_001\thyroid_balanced_6000_clean.csv.xls")

X = df.drop("target", axis=1)
y = df["target"]

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.25,
    random_state=42,
    stratify=y_encoded
)

# ✅ Pipeline with Scaling + XGBoost
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="mlogloss"
    ))
])

print("Training improved XGBoost model...")
pipeline.fit(X_train, y_train)

# Evaluate
y_pred = pipeline.predict(X_test)

print("\n📊 IMPROVED MODEL PERFORMANCE:\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))

# ✅ FORCE SAVE MODEL TO BACKEND FOLDER
model_path = r"C:\Thyroid_001\backend_001\thyroid_model1.pkl"
label_path = r"C:\Thyroid_001\backend_001\label_encoder1.pkl"

joblib.dump(pipeline, model_path)
joblib.dump(le, label_path)

print("\n✅ Improved model saved successfully!")
print("Model saved at :", model_path)
print("Label encoder saved at :", label_path)
