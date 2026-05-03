from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import pandas as pd
import joblib
import numpy as np
import re
import base64
import urllib.request
import os
from werkzeug.utils import secure_filename
import tempfile
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Paths - Update these to match your actual paths
YOLO_MODEL_PATH = "runs/detect/train2/weights/best.pt"
REPAIR_TIME_MODEL = "Work_Model/rf_repair_time_model.pkl"
BUDGET_MODEL = "Work_Model/rf_budget_model.pkl"
LE_TIME = "Work_Model/le_repair_time.pkl"
LE_BUDGET = "Work_Model/le_budget.pkl"

# Load models
print("Loading YOLO model...")
model = YOLO(YOLO_MODEL_PATH)

print("Loading ML models...")
rf_time = joblib.load(REPAIR_TIME_MODEL)
rf_budget = joblib.load(BUDGET_MODEL)
le_time = joblib.load(LE_TIME)
le_budget = joblib.load(LE_BUDGET)

# Create temp directory for downloads
TEMP_DIR = tempfile.mkdtemp()
print(f"Temp directory created at: {TEMP_DIR}")

def parse_hours(time_range):
    """Parse time range string to average hours"""
    match = re.findall(r'[\d\.]+', time_range)
    if 'hour' in time_range:
        return (float(match[0]) + float(match[1])) / 2
    elif 'day' in time_range:
        return ((float(match[0]) + float(match[1])) / 2) * 24
    return 0

def parse_budget(budget_range):
    """Parse budget range string to average value"""
    match = re.findall(r'[\d,]+', budget_range)
    low = int(match[0].replace(',', ''))
    high = int(match[1].replace(',', ''))
    return (low + high) / 2

def download_image(image_url):
    """Download image from URL and save to temp file"""
    try:
        # Generate a unique filename
        filename = secure_filename(image_url.split('/')[-1])
        if not filename or '.' not in filename:
            filename = f"image_{hash(image_url)}.jpg"
        
        local_path = os.path.join(TEMP_DIR, filename)
        
        # Download the image
        urllib.request.urlretrieve(image_url, local_path)
        return local_path
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

@app.route('/predict-file', methods=['POST'])
def predict_file():
    """
    Endpoint to predict from uploaded image file
    Expects multipart/form-data with 'image' field containing the image file
    """
    try:
        # Check if image file is present in request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({"error": "No image file selected"}), 400
        
        # Save uploaded file to temp directory
        filename = secure_filename(file.filename)
        local_image_path = os.path.join(TEMP_DIR, f"upload_{int(time.time())}_{filename}")
        file.save(local_image_path)
        
        print(f"Processing uploaded file: {local_image_path}")
        
        # Run YOLO prediction (same as before)
        results = model.predict(
            source=local_image_path,
            imgsz=640,
            conf=0.5,
            save=False,
            show=False
        )
        
        # Check if any objects detected
        if not results[0].boxes or len(results[0].boxes) == 0:
            os.remove(local_image_path)
            return jsonify({
                "detections": [],
                "summary": {
                    "damage_count": 0,
                    "total_count": 0,
                    "total_hours": 0,
                    "total_budget": 0
                },
                "annotated_image": "",
                "message": "No damage detected"
            })
        
        # Load image for annotation
        img = cv2.imread(local_image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        detections = []
        damage_count = 0
        total_hours = 0
        total_budget = 0
        
        for box in results[0].boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            
            # Get class name (damage type)
            class_name = model.names[cls]
            
            # Count damages
            damage_count += 1
            
            # Calculate bounding box ratios for ML features
            x1, y1, x2, y2 = xyxy
            width = x2 - x1
            height = y2 - y1
            img_h, img_w = img.shape[:2]
            area_ratio = (width * height) / (img_w * img_h)
            width_ratio = width / img_w
            height_ratio = height / img_h
            
            # Prepare features for ML models
            features = pd.DataFrame([{
                "class_id": cls,
                "area_ratio": area_ratio,
                "width_ratio": width_ratio,
                "height_ratio": height_ratio
            }])
            
            # Predict repair time & budget
            pred_time = le_time.inverse_transform(rf_time.predict(features))[0]
            pred_budget = le_budget.inverse_transform(rf_budget.predict(features))[0]
            
            # Parse to numeric values
            hours = parse_hours(pred_time)
            budget = parse_budget(pred_budget)
            
            total_hours += hours
            total_budget += budget
            
            detection = {
                "class_name": class_name,
                "class_id": cls,
                "confidence": round(conf, 2),
                "box": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)],
                "repair_time": pred_time,
                "budget": pred_budget,
                "hours": round(hours, 2),
                "budget_lkr": int(budget)
            }
            detections.append(detection)
            
            # Draw bounding box
            if 'pothole' in class_name.lower():
                color = (0, 0, 255)  # Red for potholes
            elif 'crack' in class_name.lower():
                color = (0, 255, 255)  # Yellow for cracks
            elif 'rut' in class_name.lower() or 'depression' in class_name.lower():
                color = (255, 165, 0)  # Orange for ruts/depressions
            else:
                color = (255, 0, 0)  # Blue for other damages
            
            cv2.rectangle(img_rgb, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            
            # Add label with confidence
            label = f"{class_name} ({conf:.2f})"
            cv2.putText(img_rgb, label, (int(x1), int(y1)-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Convert annotated image to base64
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
        annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Create summary
        summary = {
            "damage_count": damage_count,
            "total_count": damage_count,
            "total_hours": round(total_hours, 2),
            "total_budget": int(total_budget)
        }
        
        # Clean up temp file
        os.remove(local_image_path)
        
        return jsonify({
            "detections": detections,
            "summary": summary,
            "annotated_image": annotated_image_base64,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "models_loaded": True
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)