import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib


# Load dataset
df = pd.read_csv("WorkDataset/Dataset.csv")

# Features
X = df[["class_id", "area_ratio", "width_ratio", "height_ratio"]]

# Targets
y_time = df["repair_time_range"]
y_budget = df["budget_range"]


# Encode categorical targets
le_time = LabelEncoder()
y_time_enc = le_time.fit_transform(y_time)

le_budget = LabelEncoder()
y_budget_enc = le_budget.fit_transform(y_budget)


# Train/test split

X_train, X_test, y_time_train, y_time_test, y_budget_train, y_budget_test = train_test_split(
    X, y_time_enc, y_budget_enc, test_size=0.2, random_state=42
)


# Train RandomForest for repair_time
rf_time = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
rf_time.fit(X_train, y_time_train)


# Train RandomForest for budget
rf_budget = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
rf_budget.fit(X_train, y_budget_train)


# Predictions & evaluation

y_time_pred = rf_time.predict(X_test)
y_budget_pred = rf_budget.predict(X_test)

print("-->  Repair Time Prediction Accuracy:", accuracy_score(y_time_test, y_time_pred))
print("Classification Report (Repair Time):\n", classification_report(y_time_test, y_time_pred))

print("-->  Budget Prediction Accuracy:", accuracy_score(y_budget_test, y_budget_pred))
print("Classification Report (Budget):\n", classification_report(y_budget_test, y_budget_pred))


# Save models 

joblib.dump(rf_time, "Work_Model/rf_repair_time_model.pkl")
joblib.dump(rf_budget, "Work_Model/rf_budget_model.pkl")
joblib.dump(le_time, "Work_Model/le_repair_time.pkl")
joblib.dump(le_budget, "Work_Model/le_budget.pkl")

print("-->  Models and encoders saved successfully")
