import os
import joblib
import pandas as pd
import numpy as np

from sklearn.metrics import classification_report, accuracy_score

# Paths to validation data and artifacts
VAL_PATH = os.path.join("data_sarma", "labeled_sarma", "complaints_val_sa.csv")
ARTIFACT_DIR = os.path.join("artifacts_sarma")

# Function to load and clean data
def load_and_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.astype(str).str.strip()

    df["text"] = df["text"].astype(str).fillna("").str.strip()
    df = df[df["text"].str.len() > 0].copy()
    return df

# Main validation function
def main():
    df = load_and_clean(VAL_PATH)

    X = df["text"].values
    y_main = df["main_category"].values
    y_sub = df["sub_category"].values
    y_pri = df["priority_level"].astype(str).str.strip().values


    # Load artifacts
    vectorizer = joblib.load(os.path.join(ARTIFACT_DIR, "tfidf_vectorizer.joblib"))

    main_model = joblib.load(os.path.join(ARTIFACT_DIR, "main_category_model.joblib"))
    sub_model = joblib.load(os.path.join(ARTIFACT_DIR, "sub_category_model.joblib"))
    pri_model = joblib.load(os.path.join(ARTIFACT_DIR, "priority_level_model.joblib"))

    main_enc = joblib.load(os.path.join(ARTIFACT_DIR, "main_category_encoder.joblib"))
    sub_enc = joblib.load(os.path.join(ARTIFACT_DIR, "sub_category_encoder.joblib"))
    pri_enc = joblib.load(os.path.join(ARTIFACT_DIR, "priority_level_encoder.joblib"))

    X_vec = vectorizer.transform(X)

    def evaluate(name, model, y_true, encoder):
        # Predict labels 
        y_pred_enc = model.predict(X_vec)
        y_pred = encoder.inverse_transform(y_pred_enc)

        # Clean labels for reporting 
        y_true = pd.Series(y_true).astype(str).str.strip().values
        y_pred = pd.Series(y_pred).astype(str).str.strip().values

        acc = accuracy_score(y_true, y_pred)
        print("\n==============================")
        print(f"{name} (VAL) Accuracy: {acc:.4f}")
        print("==============================")
        print(classification_report(y_true, y_pred, zero_division=0))

    evaluate("Main Category", main_model, y_main, main_enc)
    evaluate("Sub Category", sub_model, y_sub, sub_enc)
    evaluate("Priority Level", pri_model, y_pri, pri_enc)


if __name__ == "__main__":
    main()
