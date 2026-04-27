import os
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge

TRAIN_PATH = os.path.join("sarma_ml", "data_sarma", "labeled_sarma", "complaints_train_sa.csv")
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


def train_and_save():
    df = load_and_clean(TRAIN_PATH)

    X = df["text"].values
    y = df["severity_score"].values

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=20000
    )

    X_vec = vectorizer.fit_transform(X)

    severity_model = Ridge(alpha=1.0)
    severity_model.fit(X_vec, y)

    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    joblib.dump(vectorizer, os.path.join(ARTIFACT_DIR, "tfidf_vectorizer_severity.joblib"))
    joblib.dump(severity_model, os.path.join(ARTIFACT_DIR, "text_severity_model.joblib"))

    print("Text severity model training finished.")
    print("Artifacts saved to:", ARTIFACT_DIR)


if __name__ == "__main__":
    train_and_save()