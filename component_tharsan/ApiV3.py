from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import pandas as pd
import joblib
import numpy as np
import re
import base64
import os
import tempfile
import time
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# =========================
# PATHS
# =========================
YOLO_MODEL_PATH = "runs/detect/train2/weights/best.pt"

REPAIR_TIME_MODEL = "Work_Model/rf_repair_time_model.pkl"
BUDGET_MODEL = "Work_Model/rf_budget_model.pkl"
LE_TIME = "Work_Model/le_repair_time.pkl"
LE_BUDGET = "Work_Model/le_budget.pkl"

# =========================
# LOAD MODELS
# =========================
model = YOLO(YOLO_MODEL_PATH)

rf_time = joblib.load(REPAIR_TIME_MODEL)
rf_budget = joblib.load(BUDGET_MODEL)
le_time = joblib.load(LE_TIME)
le_budget = joblib.load(LE_BUDGET)

TEMP_DIR = tempfile.mkdtemp()

# =========================
# UTILITIES
# =========================
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

# =========================
# ENGINEER ESTIMATE (DYNAMIC)
# =========================
def build_engineer_estimate(total_budget):

    A = total_budget * 0.05
    B = total_budget
    C = A + B
    D = C * 0.10
    E = C * 0.02
    F = C + D + E
    G = F * 0.18
    H = C * 0.02
    I = F + G + H

    return {
        "A": {"description": "Preliminaries (5%)", "amount": A},
        "B": {"description": "Construction Works (AI Prediction)", "amount": B},
        "C": {"description": "Total Civil Cost", "amount": C},
        "D": {"description": "Physical Contingencies (10%)", "amount": D},
        "E": {"description": "Price Contingencies (2%)", "amount": E},
        "F": {"description": "Sub Total", "amount": F},
        "G": {"description": "VAT (18%)", "amount": G},
        "H": {"description": "Administration Cost (2%)", "amount": H},
        "I": {"description": "Final Project Estimate", "amount": I}
    }

# =========================
# MAIN API
# =========================
@app.route('/predict-file', methods=['POST'])
def predict_file():

    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']

        filename = secure_filename(file.filename)
        local_path = os.path.join(TEMP_DIR, f"{int(time.time())}_{filename}")
        file.save(local_path)

        # =========================
        # YOLO PREDICTION
        # =========================
        results = model.predict(
            source=local_path,
            imgsz=640,
            conf=0.5,
            save=False,
            show=False
        )

        if not results[0].boxes:
            return jsonify({
                "status": "success",
                "detections": [],
                "summary": {
                    "damage_count": 0,
                    "total_hours": 0,
                    "total_budget": 0
                },
                "engineer_estimate": [],
                "final_estimate": 0,
                "annotated_image": "",
                "message": "No damage detected"
            })

        img = cv2.imread(local_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        detections = []
        total_hours = 0
        total_budget = 0

        # =========================
        # PROCESS DETECTIONS
        # =========================
        for box in results[0].boxes:

            cls = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            h, w = img.shape[:2]

            features = pd.DataFrame([{
                "class_id": cls,
                "area_ratio": ((x2-x1)*(y2-y1)) / (w*h),
                "width_ratio": (x2-x1) / w,
                "height_ratio": (y2-y1) / h
            }])

            pred_time = le_time.inverse_transform(rf_time.predict(features))[0]
            pred_budget = le_budget.inverse_transform(rf_budget.predict(features))[0]

            hours = parse_hours(pred_time)
            budget = parse_budget(pred_budget)

            total_hours += hours
            total_budget += budget

            detections.append({
                "class_name": model.names[cls],
                "confidence": round(conf, 2),
                "repair_time": pred_time,
                "budget_lkr": int(budget),
                "hours": round(hours, 2)
            })

            cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)

        # =========================
        # SUMMARY
        # =========================
        summary = {
            "damage_count": len(detections),
            "total_hours": round(total_hours, 2),
            "total_budget": int(total_budget)
        }

        # =========================
        # ENGINEER ESTIMATE
        # =========================
        engineer = build_engineer_estimate(total_budget)

        engineer_estimate = []
        for k, v in engineer.items():
            engineer_estimate.append({
                "item": k,
                "description": v["description"],
                "amount": round(v["amount"], 2)
            })

        final_estimate = round(engineer["I"]["amount"], 2)

        # =========================
        # IMAGE OUTPUT
        # =========================
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        os.remove(local_path)

        # =========================
        # FINAL RESPONSE (UI READY)
        # =========================
        return jsonify({
            "status": "success",
            "detections": detections,
            "summary": summary,
            "engineer_estimate": engineer_estimate,
            "final_estimate": final_estimate,
            "annotated_image": image_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)