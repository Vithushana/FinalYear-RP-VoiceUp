import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import confusion_matrix, mean_absolute_error, mean_squared_error, r2_score


VAL_PATH = os.path.join("sarma_ml", "data_sarma", "labeled_sarma", "complaints_val_sa.csv")
ARTIFACT_DIR = os.path.join("sarma_ml", "artifacts_sarma")
RESULTS_DIR = os.path.join("sarma_ml", "results_sarma")


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
        return "High"
    elif score >= 15:
        return "Medium"
    return "Low"


def ensure_results_dir() -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)


def load_model_and_predict(df: pd.DataFrame):
    vectorizer_path = os.path.join(ARTIFACT_DIR, "tfidf_vectorizer_severity.joblib")
    model_path = os.path.join(ARTIFACT_DIR, "text_severity_model.joblib")

    if not os.path.exists(vectorizer_path):
        raise FileNotFoundError(f"Missing file: {vectorizer_path}")

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Missing file: {model_path}")

    vectorizer = joblib.load(vectorizer_path)
    model = joblib.load(model_path)

    X_vec = vectorizer.transform(df["text"].values)
    y_true = df["severity_score"].values
    y_pred = model.predict(X_vec)

    # Keep prediction range same as your text severity design: 0-40
    y_pred = np.clip(y_pred, 0, 40)

    return y_true, y_pred


def plot_metrics_bar_chart(mae: float, rmse: float, r2: float, bucket_acc: float) -> None:
    labels = ["MAE", "RMSE", "R2", "Bucket Accuracy"]
    values = [mae, rmse, r2, bucket_acc]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values)

    plt.title("Validation Performance of ML-based Text Severity Model")
    plt.ylabel("Metric Value")
    plt.ylim(0, max(values) + 1)

    for bar, value in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.05,
            f"{value:.4f}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, "text_severity_metrics_bar_chart.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_actual_vs_predicted(y_true: np.ndarray, y_pred: np.ndarray) -> None:
    plt.figure(figsize=(7, 7))
    plt.scatter(y_true, y_pred, alpha=0.7)

    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())

    plt.plot([min_val, max_val], [min_val, max_val], linestyle="--")
    plt.xlabel("Actual Severity Score")
    plt.ylabel("Predicted Severity Score")
    plt.title("Actual vs Predicted Text Severity Scores")

    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, "actual_vs_predicted_scatter.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_bucket_confusion_matrix(y_true_bucket: list[str], y_pred_bucket: list[str]) -> None:
    labels = ["Low", "Medium", "High"]
    cm = confusion_matrix(y_true_bucket, y_pred_bucket, labels=labels)

    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation="nearest")
    plt.title("Severity Bucket Confusion Matrix")
    plt.colorbar()

    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels)
    plt.yticks(tick_marks, labels)
    plt.xlabel("Predicted Bucket")
    plt.ylabel("Actual Bucket")

    threshold = cm.max() / 2 if cm.max() > 0 else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            plt.text(
                j, i, str(cm[i, j]),
                ha="center", va="center",
                color="white" if cm[i, j] > threshold else "black"
            )

    plt.tight_layout()
    out_path = os.path.join(RESULTS_DIR, "severity_bucket_confusion_matrix.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def main() -> None:
    ensure_results_dir()

    df = load_and_clean(VAL_PATH)
    y_true, y_pred = load_model_and_predict(df)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    y_true_bucket = [bucketize(v) for v in y_true]
    y_pred_bucket = [bucketize(v) for v in y_pred]
    bucket_acc = np.mean([a == b for a, b in zip(y_true_bucket, y_pred_bucket)])

    print("\nValidation Metrics")
    print("------------------")
    print(f"MAE            : {mae:.4f}")
    print(f"RMSE           : {rmse:.4f}")
    print(f"R2             : {r2:.4f}")
    print(f"Bucket Accuracy: {bucket_acc:.4f}")

    plot_metrics_bar_chart(mae, rmse, r2, bucket_acc)
    plot_actual_vs_predicted(y_true, y_pred)
    plot_bucket_confusion_matrix(y_true_bucket, y_pred_bucket)

    print("\nAll research graphs generated successfully.")


if __name__ == "__main__":
    main()