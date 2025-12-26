import os

from flask import Flask, request, render_template_string
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# ====== Config ======
CLASS_NAMES = ["ai", "real"]  # train.py la print aana order-ku match aaganum
MODEL_WEIGHTS_PATH = os.path.join("models", "resnet50_ai_vs_real.pth")
# ====================


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_transform():
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])


def build_model(num_classes=len(CLASS_NAMES)):
    # Same architecture as train.py, but weights=None (we load our own)
    model = models.resnet50(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model


def load_model(weights_path, device):
    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"Model weights not found: {weights_path}")

    model = build_model()
    state = torch.load(weights_path, map_location=device)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    return model


def predict_image_file(file_storage, model, device):
    """
    file_storage = request.files['image'] maadhiri one file.
    """
    transform = get_transform()

    image = Image.open(file_storage.stream).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)  # [1, C, H, W]

    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        pred_idx = torch.argmax(probs).item()
        pred_label = CLASS_NAMES[pred_idx]
        pred_conf = probs[pred_idx].item()

    return pred_label, pred_conf


# ===== Flask app setup =====
app = Flask(__name__)

device = get_device()
print(f"Using device: {device}")

model = load_model(MODEL_WEIGHTS_PATH, device)
print("Model loaded successfully.")


HTML_PAGE = """
<!doctype html>
<html>
<head>
  <title>AI vs Real Image Detector</title>
  <style>
    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0f172a;
      color: #e5e7eb;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      margin: 0;
    }
    .card {
      background: #020617;
      border-radius: 16px;
      padding: 24px 28px;
      max-width: 480px;
      width: 100%;
      box-shadow: 0 20px 40px rgba(0,0,0,0.5);
      border: 1px solid #1f2937;
    }
    h1 {
      margin-top: 0;
      font-size: 1.4rem;
      margin-bottom: 0.5rem;
    }
    p {
      margin-top: 0;
      margin-bottom: 1rem;
      color: #9ca3af;
      font-size: 0.9rem;
    }
    .file-input {
      margin: 12px 0;
    }
    .btn {
      margin-top: 8px;
      background: #2563eb;
      border: none;
      color: white;
      padding: 8px 16px;
      border-radius: 999px;
      cursor: pointer;
      font-size: 0.9rem;
    }
    .btn:hover {
      background: #1d4ed8;
    }
    .result {
      margin-top: 16px;
      padding: 12px 14px;
      border-radius: 10px;
      font-size: 0.9rem;
    }
    .result-ai {
      background: rgba(220, 38, 38, 0.15);
      border: 1px solid #ef4444;
    }
    .result-real {
      background: rgba(22, 163, 74, 0.15);
      border: 1px solid #22c55e;
    }
    .label-pill {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 0.75rem;
      margin-bottom: 4px;
    }
    .label-ai {
      background: #450a0a;
      color: #fecaca;
    }
    .label-real {
      background: #052e16;
      color: #bbf7d0;
    }
    .confidence {
      color: #9ca3af;
      font-size: 0.8rem;
      margin-top: 4px;
    }
    .error {
      margin-top: 12px;
      color: #fecaca;
      font-size: 0.85rem;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>AI vs Real Image Detector</h1>
    <p>Upload one image to check whether it is likely <strong>AI-generated</strong> or a <strong>real camera photo</strong>.</p>

    <form method="POST" enctype="multipart/form-data">
      <div class="file-input">
        <input type="file" name="image" accept="image/*" required />
      </div>
      <button type="submit" class="btn">Check Image</button>
    </form>

    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}

    {% if label %}
      <div class="result {% if label == 'ai' %}result-ai{% else %}result-real{% endif %}">
        <div class="label-pill {% if label == 'ai' %}label-ai{% else %}label-real{% endif %}">
          {{ label.upper() }}
        </div>
        <div>
          {% if label == 'ai' %}
            This image is likely <strong>AI-generated</strong>.
          {% else %}
            This image is likely a <strong>REAL camera photo</strong>.
          {% endif %}
        </div>
        <div class="confidence">
          Confidence: {{ confidence }}%
        </div>
      </div>
    {% endif %}
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    label = None
    confidence = None

    if request.method == "POST":
        file = request.files.get("image")
        if not file or file.filename == "":
            error = "Please choose an image file."
        else:
            try:
                pred_label, pred_conf = predict_image_file(file, model, device)
                label = pred_label
                confidence = f"{pred_conf * 100:.2f}"
            except Exception as e:
                print("Error during prediction:", e)
                error = "Something went wrong while processing the image."

    return render_template_string(HTML_PAGE, error=error, label=label, confidence=confidence)


if __name__ == "__main__":
    # debug=True nu local dev-ku ok; deployment-ku off pannalaam
    app.run(host="127.0.0.1", port=5013, debug=True)
