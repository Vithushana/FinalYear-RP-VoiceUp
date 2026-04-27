import csv
import os
import random
from datetime import datetime

from dataset_templated_sa import TEMPLATES
from text_variation_utils_sa import (
    make_variation,
    make_ambiguous_text,
    expand_complaint_text,
)

RANDOM_SEED = 42
VARIATIONS_PER_BASE = 6


def clamp_score(value: int, min_value: int = 0, max_value: int = 40) -> int:
    return max(min_value, min(max_value, int(value)))


def adjust_severity_for_variation(text: str, base_score: int) -> int:
    """
    Optional small adjustment so all generated rows are not perfectly identical in score.
    Keeps score in 0-40 range.
    """
    t = (text or "").lower()
    score = int(base_score)

    high_keywords = [
        "urgent", "danger", "accident", "ambulance", "hospital",
        "school", "blocked", "cannot pass", "health risk",
        "mosquito", "disease", "rats"
    ]

    medium_keywords = [
        "traffic", "difficult", "inconvenience", "bad smell",
        "overflow", "damaged", "broken"
    ]

    frequency_keywords = [
        "daily", "every day", "frequently", "repeated",
        "again and again", "many days"
    ]

    if any(k in t for k in high_keywords):
        score += 2
    elif any(k in t for k in medium_keywords):
        score += 1

    if any(k in t for k in frequency_keywords):
        score += 1

    return clamp_score(score)


def generate_rows():
    rows = []

    # NEW:
    # template format:
    # (main_category, sub_category, priority_level, severity_score, bases)
    for main_category, sub_category, priority_level, severity_score, bases in TEMPLATES:
        for base in bases:
            for _ in range(VARIATIONS_PER_BASE):
                v = make_variation(base)
                v = make_ambiguous_text(main_category, v)

                v_score = adjust_severity_for_variation(v, severity_score)

                rows.append({
                    "text": v,
                    "main_category": main_category,
                    "sub_category": sub_category,
                    "priority_level": str(priority_level),
                    "severity_score": v_score
                })

                expanded = expand_complaint_text(main_category, v)
                expanded_score = adjust_severity_for_variation(expanded, severity_score)

                rows.append({
                    "text": expanded,
                    "main_category": main_category,
                    "sub_category": sub_category,
                    "priority_level": str(priority_level),
                    "severity_score": expanded_score
                })

    # remove duplicates
    unique = {}
    for r in rows:
        key = (
            r["text"],
            r["main_category"],
            r["sub_category"],
            r["priority_level"],
            r["severity_score"],
        )
        unique[key] = r

    rows = list(unique.values())
    random.shuffle(rows)
    return rows


def main():
    random.seed(RANDOM_SEED)

    out_dir = os.path.join("sarma_ml", "data_sarma", "labeled_sarma")
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, "complaints_training_sa.csv")

    rows = generate_rows()

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "text",
                "main_category",
                "sub_category",
                "priority_level",
                "severity_score"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("Realistic dataset with severity_score created!")
    print("File:", out_path)
    print("Total rows:", len(rows))
    print("Generated at:", datetime.now().isoformat(timespec="seconds"))


if __name__ == "__main__":
    main()