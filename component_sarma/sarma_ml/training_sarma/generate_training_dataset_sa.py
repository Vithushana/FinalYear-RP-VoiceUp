
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

def generate_rows():
    rows = []
    for main_category, sub_category, priority_level, bases in TEMPLATES:
        for base in bases:
            for _ in range(VARIATIONS_PER_BASE):
                v = make_variation(base)
                v = make_ambiguous_text(main_category, v)

                rows.append({
                    "text": v,
                    "main_category": main_category,
                    "sub_category": sub_category,
                    "priority_level": str(priority_level)
                })

                expanded = expand_complaint_text(main_category, v)
                rows.append({
                    "text": expanded,
                    "main_category": main_category,
                    "sub_category": sub_category,
                    "priority_level": str(priority_level)
                })

    # remove duplicates
    unique = {}
    for r in rows:
        key = (r["text"], r["main_category"], r["sub_category"], r["priority_level"])
        unique[key] = r

    rows = list(unique.values())
    random.shuffle(rows)
    return rows

def main():
    random.seed(RANDOM_SEED)

    out_dir = os.path.join("data_sarma", "labeled_sarma")
    os.makedirs(out_dir, exist_ok=True)

    out_path = os.path.join(out_dir, "complaints_training_sa.csv")

    rows = generate_rows()

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["text", "main_category", "sub_category", "priority_level"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("Realistic dataset created!")
    print("File:", out_path)
    print("Total rows:", len(rows))
    print("Generated at:", datetime.now().isoformat(timespec="seconds"))

if __name__ == "__main__":
    main()
