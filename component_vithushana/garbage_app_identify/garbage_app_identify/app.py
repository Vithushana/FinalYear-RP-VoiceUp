from flask import Flask, request, render_template, jsonify
from ultralytics import YOLO
import os, uuid
import cv2
import base64
import io
from PIL import Image

app = Flask(__name__)

MODEL_PATH = "best.pt"
# model cache for multiple model variants (e.g., YOLOv8, YOLOv11)
_MODELS = {}

def get_model(path_key: str):
    """Return a YOLO model instance for the given path/key, caching instances."""
    # map friendly keys to actual filenames
    mapping = {
        "default": MODEL_PATH,
        "yolov11": "best_v11.pt",  # user can place a YOLOv11 weights file here
    }
    model_path = mapping.get(path_key, path_key)
    # if absolute or relative path provided, use it directly
    if model_path not in _MODELS:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model weights not found: {model_path}")
        _MODELS[model_path] = YOLO(model_path)
    return _MODELS[model_path]

# ensure default model loaded at startup (but don't crash if missing)
try:
    _MODELS[MODEL_PATH] = YOLO(MODEL_PATH)
except Exception:
    # lazy load on first request
    pass

UPLOAD_DIR = os.path.join("static", "uploads")
RESULT_DIR = os.path.join("static", "results")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# Environmental advice for each garbage type
GARBAGE_ADVICE = {
    "PLASTIC": {
        "severity": "high",
        "advice": "🚨 NOT GOOD FOR THE ENVIRONMENT!",
        "details": "Plastic takes 400+ years to decompose. It pollutes oceans and harms wildlife.",
        "action": "❌ DO NOT LITTER - Remove immediately and recycle properly!",
        "tips": "• Avoid single-use plastics\n• Use reusable bags & bottles\n• Recycle at designated centers"
    },
    "GLASS": {
        "severity": "medium",
        "advice": "⚠️ HANDLE WITH CARE!",
        "details": "Glass takes 1 million years to decompose but is recyclable.",
        "action": "♻️ Recycle in glass bins - DO NOT discard as regular trash",
        "tips": "• Rinse before recycling\n• Separate by color if required\n• Check local recycling guidelines"
    },
    "METAL": {
        "severity": "medium",
        "advice": "♻️ RECYCLABLE MATERIAL",
        "details": "Metal can be recycled infinitely without losing quality.",
        "action": "✅ Collect and recycle at metal recycling centers",
        "tips": "• Metal recycling reduces mining needs\n• Reduces energy consumption by 90%\n• Valuable material - may earn money!"
    },
    "CARDBOARD": {
        "severity": "low",
        "advice": "✅ BIODEGRADABLE",
        "details": "Cardboard decomposes in 2-8 months and is easily recyclable.",
        "action": "📦 Flatten and recycle with paper products",
        "tips": "• Remove any plastic or tape\n• Keep dry when storing\n• Great for compost too"
    },
    "PAPER": {
        "severity": "low",
        "advice": "✅ BIODEGRADABLE",
        "details": "Paper decomposes in 2-6 weeks naturally.",
        "action": "📰 Add to paper recycling or compost",
        "tips": "• Reuse paper for notes\n• Shred for packaging material\n• Compostable in gardens"
    },
    "BIODEGRADABLE": {
        "severity": "low",
        "advice": "✅ NATURAL & SAFE",
        "details": "Organic waste decomposes naturally within weeks to months.",
        "action": "🌱 Compost or dispose naturally",
        "tips": "• Start a compost pile\n• Food waste reduces methane in landfills\n• Nutrient-rich for gardens"
    }
}

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/predict")
def predict():
    # Handle both file upload and JSON base64 data (for inter-service calls)
    image_data = None
    image_filename = None
    
    # Check for file upload first
    if "image" in request.files:
        f = request.files["image"]
        if f.filename != "":
            image_data = f.read()
            image_filename = f.filename
    
    # Check for JSON base64 data (from port 5002)
    elif request.is_json:
        data = request.get_json()
        if "image" in data:
            # Handle base64 image data
            base64_image = data["image"]
            if "," in base64_image:
                base64_image = base64_image.split(',')[1]
            image_data = base64.b64decode(base64_image)
            image_filename = "base64_image.jpg"
    
    if image_data is None:
        return jsonify({"error": "No image provided (file or base64)"}), 400

    # Save image temporarily for YOLO processing
    uid = str(uuid.uuid4())
    safe_name = (image_filename or "image").replace(" ", "_")
    in_name = f"{uid}_{safe_name}"
    in_path = os.path.join(UPLOAD_DIR, in_name)
    
    # Convert bytes to image and save
    image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image.save(in_path)

    # Allow optional model selection (form field 'model' or JSON), default -> 'default'
    model_key = request.form.get("model", "default")
    if request.is_json:
        model_key = request.get_json().get("model", "default")
    
    try:
        use_model = get_model(model_key)
    except FileNotFoundError:
        return jsonify({"error": f"Model not found: {model_key}"}), 400

    # Predict (save=False)
    results = use_model.predict(source=in_path, conf=0.25, iou=0.5, save=False)
    r0 = results[0]

    detections = []
    for box in r0.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
        class_name = use_model.names.get(cls_id, str(cls_id))
        advice = GARBAGE_ADVICE.get(class_name, {})
        detections.append({
            "class_id": cls_id,
            "class_name": class_name,
            "confidence": conf,
            "bbox": [x1, y1, x2, y2],
            "advice": advice
        })

    # Create a deduplicated list by class name, keeping the highest-confidence detection per class
    unique_by_class = {}
    for d in detections:
        key = d["class_name"]
        if key not in unique_by_class or d["confidence"] > unique_by_class[key]["confidence"]:
            unique_by_class[key] = d
    unique_detections = list(unique_by_class.values())

    # Create result image ourselves (always consistent)
    out_folder = os.path.join(RESULT_DIR, uid)
    os.makedirs(out_folder, exist_ok=True)
    out_name = in_name  # same name
    out_path = os.path.join(out_folder, out_name)

    plotted = r0.plot()  # numpy image with boxes
    cv2.imwrite(out_path, cv2.cvtColor(plotted, cv2.COLOR_RGB2BGR))

    # URLs (must start with /static/...)
    input_url = f"/static/uploads/{in_name}"
    result_url = f"/static/results/{uid}/{out_name}"

    # OPTIONAL: single best class (highest confidence)
    best = None
    if detections:
        best = max(detections, key=lambda d: d["confidence"])

    return jsonify({
        "input_image": input_url,
        "result_image": result_url,
        "best_prediction": best,   # one final answer (optional)
        "detections": detections,
        "unique_detections": unique_detections
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
