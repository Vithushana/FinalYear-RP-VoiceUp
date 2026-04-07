import os
import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression

# Paths to training data and artifacts
TRAIN_PATH = os.path.join("data_sarma", "labeled_sarma", "complaints_train_sa.csv")
ARTIFACT_DIR = os.path.join("artifacts_sarma")

# Function to load and clean data
def load_and_clean(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    df.columns = df.columns.astype(str).str.strip()

    df["text"] = df["text"].astype(str).fillna("").str.strip()
    df = df[df["text"].str.len() > 0].copy()

    return df

# Main training function 
def train_and_save():
    df = load_and_clean(TRAIN_PATH)

    X = df["text"].values
    y_main = df["main_category"].astype(str).values
    y_sub = df["sub_category"].astype(str).values
    y_pri = df["priority_level"].astype(str).values

    # Vectorizer
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_features=20000
    )
    X_vec = vectorizer.fit_transform(X)

    # Encoders
    main_enc = LabelEncoder()
    sub_enc = LabelEncoder()
    pri_enc = LabelEncoder()

    y_main_enc = main_enc.fit_transform(y_main)
    y_sub_enc = sub_enc.fit_transform(y_sub)
    y_pri_enc = pri_enc.fit_transform(y_pri)

    # Models
    main_model = LogisticRegression(max_iter=2000)
    sub_model = LogisticRegression(max_iter=4000)
    pri_model = LogisticRegression(max_iter=2000)

    main_model.fit(X_vec, y_main_enc)
    sub_model.fit(X_vec, y_sub_enc)
    pri_model.fit(X_vec, y_pri_enc)

    # Save artifacts
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    joblib.dump(vectorizer, os.path.join(ARTIFACT_DIR, "tfidf_vectorizer.joblib"))

    joblib.dump(main_model, os.path.join(ARTIFACT_DIR, "main_category_model.joblib"))
    joblib.dump(sub_model, os.path.join(ARTIFACT_DIR, "sub_category_model.joblib"))
    joblib.dump(pri_model, os.path.join(ARTIFACT_DIR, "priority_level_model.joblib"))

    joblib.dump(main_enc, os.path.join(ARTIFACT_DIR, "main_category_encoder.joblib"))
    joblib.dump(sub_enc, os.path.join(ARTIFACT_DIR, "sub_category_encoder.joblib"))
    joblib.dump(pri_enc, os.path.join(ARTIFACT_DIR, "priority_level_encoder.joblib"))

    print("Training finished. Artifacts saved.")


if __name__ == "__main__":
    train_and_save()
