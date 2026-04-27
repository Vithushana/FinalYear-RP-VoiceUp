import os
import joblib
import pandas as pd
import numpy as np

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

VAL_PATH = os.path.join("sarma_ml", "data_sarma", "labeled_sarma", "complaints_val_sa.csv")
ARTIFACT_DIR = os.path.join("sarma_ml", "artifacts_sarma")


def load_and_clean(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    df.columns = df.columns.astype(str).str.strip()

    if "text" not in df.columns:
        raise KeyError(f"'text' column missing. Found columns: {list(df.columns)}")

    if "severity_score" not in df.columns:
        raise KeyError(f"'severity_score' column missing. Found columns: {list(df.columns)}")

    df["text"] = df["text"].astype(str).fillna("").str.strip()
    df = df[df["text"].str.len() > 0].copy()

    df["severity_score"] = pd.to_numeric(df["severity_score"], errors="coerce")
    df = df[df["severity_score"].notna()].copy()
    df["severity_score"] = df["severity_score"].astype(float)

    return df


def bucketize(score: float) -> str:
    if score >= 28:
        return "high"
    elif score >= 15:
        return "medium"
    return "low"


def main():
    df = load_and_clean(VAL_PATH)

    X = df["text"].values
    y_true = df["severity_score"].values

    vectorizer = joblib.load(os.path.join(ARTIFACT_DIR, "tfidf_vectorizer_severity.joblib"))
    model = joblib.load(os.path.join(ARTIFACT_DIR, "text_severity_model.joblib"))

    X_vec = vectorizer.transform(X)
    y_pred = model.predict(X_vec)

    y_pred = np.clip(y_pred, 0, 40)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    print("\n==============================")
    print("Text Severity Model (VAL)")
    print("==============================")
    print(f"MAE :  {mae:.4f}")
    print(f"RMSE:  {rmse:.4f}")
    print(f"R2  :  {r2:.4f}")

    y_true_bucket = [bucketize(v) for v in y_true]
    y_pred_bucket = [bucketize(v) for v in y_pred]

    bucket_acc = np.mean([a == b for a, b in zip(y_true_bucket, y_pred_bucket)])
    print(f"Bucket Accuracy (low/medium/high): {bucket_acc:.4f}")

    print("\nSample predictions:")
    preview = pd.DataFrame({
        "text": df["text"].head(10).values,
        "true_score": y_true[:10],
        "pred_score": np.round(y_pred[:10], 2),
        "true_bucket": y_true_bucket[:10],
        "pred_bucket": y_pred_bucket[:10],
    })
    print(preview.to_string(index=False))


if __name__ == "__main__":
    main()