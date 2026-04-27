import joblib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ML_ARTIFACT_DIR = PROJECT_ROOT / "sarma_ml" / "artifacts_sarma"

VECTORIZER_PATH = ML_ARTIFACT_DIR / "tfidf_vectorizer_severity.joblib"
MODEL_PATH = ML_ARTIFACT_DIR / "text_severity_model.joblib"


if not VECTORIZER_PATH.exists():
    raise FileNotFoundError(f"Severity vectorizer not found: {VECTORIZER_PATH}")

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Severity model not found: {MODEL_PATH}")


vectorizer = joblib.load(VECTORIZER_PATH)
severity_model = joblib.load(MODEL_PATH)


def clamp_score(value: float, min_value: int = 0, max_value: int = 40) -> int:
    value = round(float(value))
    return max(min_value, min(max_value, value))


def to_label(score: int) -> str:
    if score >= 28:
        return "High Text Severity"
    elif score >= 15:
        return "Medium Text Severity"
    return "Low Text Severity"


def predict_text_severity_ml(expanded_text: str) -> dict:
    """
    Predicts text severity score (0-40) from complaint text using TF-IDF + ML regression.
    """
    text = (expanded_text or "").strip()
    if not text:
        return {
            "text_severity_ml": 0,
            "severity_label": "Low Text Severity",
            "model_name": "tfidf_ridge_text_severity",
            "note": "Empty text provided."
        }

    X_vec = vectorizer.transform([text])
    raw_score = severity_model.predict(X_vec)[0]
    score = clamp_score(raw_score)

    return {
        "text_severity_ml": score,
        "severity_label": to_label(score),
        "model_name": "tfidf_ridge_text_severity",
        "note": "ML-predicted text severity score from complaint text."
    }