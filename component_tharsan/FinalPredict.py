from ultralytics import YOLO
import cv2
import pandas as pd
import joblib
import numpy as np
import re


# Paths
YOLO_MODEL_PATH = "runs/detect/train2/weights/best.pt"
IMAGE_PATH = r"test\1.jpg"

REPAIR_TIME_MODEL = "Work_Model/rf_repair_time_model.pkl"
BUDGET_MODEL = "Work_Model/rf_budget_model.pkl"
LE_TIME = "Work_Model/le_repair_time.pkl"
LE_BUDGET = "Work_Model/le_budget.pkl"


# Load models
model = YOLO(YOLO_MODEL_PATH)

rf_time = joblib.load(REPAIR_TIME_MODEL)
rf_budget = joblib.load(BUDGET_MODEL)
le_time = joblib.load(LE_TIME)
le_budget = joblib.load(LE_BUDGET)


# Utility
def parse_hours(time_range):
    match = re.findall(r'[\d\.]+', time_range)
    if 'hour' in time_range:
        return (float(match[0]) + float(match[1])) / 2
    elif 'day' in time_range:
        return ((float(match[0]) + float(match[1])) / 2) * 24
    return 0

def parse_budget(budget_range):
    match = re.findall(r'[\d,]+', budget_range)
    low = int(match[0].replace(',', ''))
    high = int(match[1].replace(',', ''))
    return (low + high) / 2


# Predict
results = model.predict(
    source=IMAGE_PATH,
    imgsz=640,
    conf=0.5,
    save=False,
    show=False
)

if not results[0].boxes or len(results[0].boxes) == 0:
    print("No objects detected")
    exit()

detections = []

img = cv2.imread(IMAGE_PATH)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


# PROCESS DETECTIONS
for box in results[0].boxes:
    cls = int(box.cls[0])
    conf = float(box.conf[0])
    x1, y1, x2, y2 = box.xyxy[0].tolist()

    width = x2 - x1
    height = y2 - y1
    img_h, img_w = img.shape[:2]

    area_ratio = (width * height) / (img_w * img_h)
    width_ratio = width / img_w
    height_ratio = height / img_h

    features = pd.DataFrame([{
        "class_id": cls,
        "area_ratio": area_ratio,
        "width_ratio": width_ratio,
        "height_ratio": height_ratio
    }])

    pred_time = le_time.inverse_transform(rf_time.predict(features))[0]
    pred_budget = le_budget.inverse_transform(rf_budget.predict(features))[0]

    hours = parse_hours(pred_time)
    budget = parse_budget(pred_budget)

    detections.append({
        "Class": model.names[cls],
        "Confidence": conf,
        "Hours": hours,
        "Budget_LKR": budget
    })

    label = f"{model.names[cls]} {conf:.2f}"
    cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
    cv2.putText(img_rgb, label, (int(x1), int(y1)-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)


# DATAFRAME
df = pd.DataFrame(detections)

print("\n=== Detected Damages ===")
print(df)


# TOTALS
total_hours = df["Hours"].sum()
total_budget = df["Budget_LKR"].sum()

print("\n=== TOTAL ESTIMATION ===")
print(f"Total Hours: {total_hours:.2f}")
print(f"Total Budget: {int(total_budget):,} LKR")


# ENGINEER ESTIMATE (

summary_rows = []

A = total_budget * 0.05
summary_rows.append(["A", "Preliminaries  ", A])

B = total_budget
summary_rows.append(["B", "Construction Works ", B])

C = A + B
summary_rows.append(["C", "Total Civil Cost ", C])
D = C * 0.10
summary_rows.append(["D", "Physical Contingencies", D])
E = C * 0.02
summary_rows.append(["E", "Price Contingencies ", E])
F = C + D + E
summary_rows.append(["F", "Sub Total", F])
G = F * 0.18
summary_rows.append(["G", "VAT ", G])
H = C * 0.02
summary_rows.append(["H", "Administration Cost", H])
I = F + G + H
summary_rows.append(["I", "Total Project Estimate", I])

summary_df = pd.DataFrame(summary_rows, columns=["Item", "Description", "Amount (LKR)"])

print("\n================ FULL ESTIMATE ================\n")
print(summary_df.to_string(index=False))

print("\n===================================================")
print(f"FINAL ESTIMATE: {int(I):,} LKR")
print("===================================================")


# SHOW IMAGE
annotated_image = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
cv2.imshow("YOLO + AI Engineer Estimate", annotated_image)
cv2.waitKey(0)
cv2.destroyAllWindows()