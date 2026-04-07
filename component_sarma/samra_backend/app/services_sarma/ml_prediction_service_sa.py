import os
import joblib
import numpy as np
from pathlib import Path

# Path to ML artifacts
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ML_ARTIFACT_DIR = PROJECT_ROOT / "sarma_ml" / "artifacts_sarma"

# Load models (once)
vectorizer = joblib.load(os.path.join(ML_ARTIFACT_DIR, "tfidf_vectorizer.joblib"))

main_model = joblib.load(os.path.join(ML_ARTIFACT_DIR, "main_category_model.joblib"))
sub_model = joblib.load(os.path.join(ML_ARTIFACT_DIR, "sub_category_model.joblib"))
pri_model = joblib.load(os.path.join(ML_ARTIFACT_DIR, "priority_level_model.joblib"))

main_encoder = joblib.load(os.path.join(ML_ARTIFACT_DIR, "main_category_encoder.joblib"))
sub_encoder = joblib.load(os.path.join(ML_ARTIFACT_DIR, "sub_category_encoder.joblib"))
pri_encoder = joblib.load(os.path.join(ML_ARTIFACT_DIR, "priority_level_encoder.joblib"))


def predict_from_text(expanded_text: str) -> dict:
    """
    Takes expanded complaint text and returns ML predictions
    """

    # Vectorize
    X_vec = vectorizer.transform([expanded_text])

    # Predict encoded values
    main_pred_enc = main_model.predict(X_vec)[0]
    sub_pred_enc = sub_model.predict(X_vec)[0]
    pri_pred_enc = pri_model.predict(X_vec)[0]

    # Decode labels
    main_pred = main_encoder.inverse_transform([main_pred_enc])[0]
    sub_pred = sub_encoder.inverse_transform([sub_pred_enc])[0]
    pri_pred = int(pri_encoder.inverse_transform([pri_pred_enc])[0])

    # Confidence (simple, explainable)
    main_conf = float(np.max(main_model.predict_proba(X_vec)))
    sub_conf = float(np.max(sub_model.predict_proba(X_vec)))
    pri_conf = float(np.max(pri_model.predict_proba(X_vec)))

    confidence = round((main_conf + sub_conf + pri_conf) / 3, 2)

    return {
        "main_category_ml": main_pred,
        "sub_category_ml": sub_pred,
        "priority_level_ml": pri_pred,
        "confidence": confidence
    }
