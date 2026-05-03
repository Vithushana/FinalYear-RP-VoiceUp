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
import uuid
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
try:
    model = YOLO(YOLO_MODEL_PATH)
    print("✅ Road damage detection model loaded")
except Exception as e:
    print(f"❌ Road damage detection model not available: {e}")
    model = None

try:
    rf_time = joblib.load(REPAIR_TIME_MODEL)
    rf_budget = joblib.load(BUDGET_MODEL)
    le_time = joblib.load(LE_TIME)
    le_budget = joblib.load(LE_BUDGET)
    print("✅ Repair time & budget estimation models loaded")
except Exception as e:
    print(f"❌ Estimation models not available: {e}")
    rf_time = rf_budget = le_time = le_budget = None

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


def save_base64_image_to_temp(image_base64):
    """Decode base64 image payload and save it to a temp file path."""
    if not image_base64 or not isinstance(image_base64, str):
        raise ValueError("Invalid image payload")

    # Support optional data URI prefixes: data:image/jpeg;base64,....
    if ',' in image_base64 and image_base64.strip().lower().startswith('data:image'):
        image_base64 = image_base64.split(',', 1)[1]

    image_bytes = base64.b64decode(image_base64)
    filename = f"json_{uuid.uuid4().hex}.jpg"
    local_path = os.path.join(TEMP_DIR, filename)

    with open(local_path, 'wb') as f:
        f.write(image_bytes)

    return local_path

# =========================
# ENGINEER ESTIMATE (DYNAMIC)
# =========================
def scale_construction_budget(raw_budget):
    if raw_budget <= 15000:
        return raw_budget
    elif raw_budget <= 25000:
        return raw_budget / 1.25
    elif raw_budget <= 30000:
        return raw_budget / 1.5
    elif raw_budget <= 50000:
        return raw_budget / 2.5
    elif raw_budget <= 60000:
        return raw_budget / 3
    elif raw_budget <= 75000:
        return raw_budget / 3.8
    else:
        return raw_budget / 6

def build_engineer_estimate(total_budget):
    
    A = total_budget * 0.05
    B = scale_construction_budget(total_budget)
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
@app.route('/predict', methods=['POST'])
def predict_json():
    """
    Backend integration endpoint.
    Expects JSON: {"image": "<base64 string>"}
    """
    try:
        data = request.get_json(silent=True) or {}
        image_base64 = data.get('image')

        if not image_base64:
            return jsonify({"error": "No base64 image provided"}), 400

        local_path = save_base64_image_to_temp(image_base64)

        results = model.predict(
            source=local_path,
            imgsz=640,
            conf=0.5,
            save=False,
            show=False
        )

        if not results[0].boxes:
            os.remove(local_path)
            return jsonify({
                "status": "success",
                "detections": [],
                "best_prediction": None,
                "message": "No damage detected"
            })

        detections = []
        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            detections.append({
                "class_name": model.names[cls],
                "confidence": round(conf, 4)
            })

        best_prediction = max(detections, key=lambda d: d["confidence"]) if detections else None

        os.remove(local_path)

        return jsonify({
            "status": "success",
            "detections": detections,
            "best_prediction": best_prediction
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

            if rf_time is not None and rf_budget is not None and le_time is not None and le_budget is not None:
                pred_time = le_time.inverse_transform(rf_time.predict(features))[0]
                pred_budget = le_budget.inverse_transform(rf_budget.predict(features))[0]
            else:
                # Fallback defaults when estimation models are unavailable
                pred_time = "4-8 hours"
                pred_budget = "50,000-100,000"

            hours = parse_hours(pred_time)
            budget = parse_budget(pred_budget)

            area_pct = round(((x2-x1)*(y2-y1)) / (w*h) * 100, 2)

            total_hours += hours
            total_budget += budget

            # ── Physical dimension estimates ──────────────────────────────
            # Assume a standard road lane width of 3.5 m fills the image width.
            ROAD_WIDTH_M = 3.5
            px_per_m = w / ROAD_WIDTH_M          # pixels per metre
            dmg_width_cm  = round((x2 - x1) / px_per_m * 100, 1)
            dmg_length_cm = round((y2 - y1) / px_per_m * 100, 1)

            # Depth heuristic: scales with area ratio and damage type
            area_ratio = ((x2-x1)*(y2-y1)) / (w*h)
            cname = model.names[cls].lower()
            if 'pothole' in cname:
                dmg_depth_cm = round(5 + area_ratio * 150, 1)   # ~5–20 cm
            elif 'crack' in cname:
                dmg_depth_cm = round(0.3 + area_ratio * 20, 1)  # ~0.3–2 cm
            else:
                dmg_depth_cm = round(0.5 + area_ratio * 10, 1)  # generic
            # ─────────────────────────────────────────────────────────────

            detections.append({
                "class_name": model.names[cls],
                "confidence": round(conf, 2),
                "repair_time": pred_time,
                "budget_lkr": int(budget),
                "hours": round(hours, 2),
                "area_pct": area_pct,
                "width_cm": dmg_width_cm,
                "length_cm": dmg_length_cm,
                "depth_cm": dmg_depth_cm
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
    print("\n" + "="*60)
    print("🚀 STARTING COMPONENT SERVICE")
    print("="*60)
    print(f"Component: Tharsan's Road Damage Detection Component")
    print(f"Port: 5003")
    print(f"Endpoints:")
    print(f"  - GET  /health        (Health check)")
    print(f"  - POST /predict       (Base64 image prediction)")
    print(f"  - POST /predict-file  (File upload prediction)")
    print(f"")
    print(f"🛣️  Road damage detection with repair time & budget estimation")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5003, debug=True)