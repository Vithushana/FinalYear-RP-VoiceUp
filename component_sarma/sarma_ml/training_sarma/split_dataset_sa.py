import os
import pandas as pd
from sklearn.model_selection import train_test_split

INPUT_CSV = os.path.join("sarma_ml", "data_sarma", "labeled_sarma", "complaints_training_sa.csv")
OUT_DIR = os.path.join("sarma_ml", "data_sarma", "labeled_sarma")

TRAIN_OUT = os.path.join(OUT_DIR, "complaints_train_sa.csv")
VAL_OUT = os.path.join(OUT_DIR, "complaints_val_sa.csv")
TEST_OUT = os.path.join(OUT_DIR, "complaints_test_sa.csv")


def pick_text_column(df: pd.DataFrame) -> str:
    candidates = ["text", "complaint_text", "text_expanded", "text_original", "sentence"]
    for c in candidates:
        if c in df.columns:
            return c

    for c in df.columns:
        if "text" in c.lower():
            return c

    raise KeyError(f"No text column found. Columns are: {list(df.columns)}")


def build_severity_bucket(series: pd.Series) -> pd.Series:
    """
    Buckets severity score for safer stratified split.
    0-14 = low, 15-27 = medium, 28-40 = high
    """
    return pd.cut(
        series.astype(int),
        bins=[-1, 14, 27, 40],
        labels=["low", "medium", "high"]
    )


def main():
    df = pd.read_csv(INPUT_CSV)
    df.columns = df.columns.astype(str).str.strip()

    text_col = pick_text_column(df)
    print(f"Using text column: {text_col}")

    df[text_col] = df[text_col].astype(str).fillna("").str.strip()
    df = df[df[text_col].str.len() > 0].copy()

    required = {"main_category", "sub_category", "priority_level", "severity_score"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required label columns: {missing}. Found columns: {list(df.columns)}")

    df["priority_level"] = df["priority_level"].astype(str).str.strip()
    df["severity_score"] = pd.to_numeric(df["severity_score"], errors="coerce")
    df = df[df["severity_score"].notna()].copy()
    df["severity_score"] = df["severity_score"].astype(int)

    df["severity_bucket"] = build_severity_bucket(df["severity_score"]).astype(str)

    # stratify key keeps a balanced distribution
    df["stratify_key"] = (
        df["main_category"].astype(str) + "|" +
        df["sub_category"].astype(str) + "|" +
        df["priority_level"].astype(str) + "|" +
        df["severity_bucket"].astype(str)
    )

    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=42,
        shuffle=True,
        stratify=df["stratify_key"]
    )

    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=42,
        shuffle=True,
        stratify=temp_df["stratify_key"]
    )

    for d in (train_df, val_df, test_df):
        d.drop(columns=["stratify_key", "severity_bucket"], inplace=True, errors="ignore")

    os.makedirs(OUT_DIR, exist_ok=True)
    train_df.to_csv(TRAIN_OUT, index=False)
    val_df.to_csv(VAL_OUT, index=False)
    test_df.to_csv(TEST_OUT, index=False)

    print("Train:", len(train_df), "->", TRAIN_OUT)
    print("Val:  ", len(val_df), "->", VAL_OUT)
    print("Test: ", len(test_df), "->", TEST_OUT)


if __name__ == "__main__":
    main()