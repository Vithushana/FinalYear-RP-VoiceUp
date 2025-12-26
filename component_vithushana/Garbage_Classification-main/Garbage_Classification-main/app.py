from flask import Flask, request, render_template, jsonify
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

app = Flask(__name__)

# -------- Load checkpoint --------
CKPT_PATH = "garbage_model.pth"
ckpt = torch.load(CKPT_PATH, map_location="cpu")
class_names = ckpt["class_names"]
IMG_SIZE = ckpt.get("img_size", 160)

# -------- Build same model arch used in training --------
model = models.mobilenet_v2(weights=None)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(class_names))
model.load_state_dict(ckpt["model_state"])
model.eval()

tfm = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
])

def predict_pil(img: Image.Image):
    img = img.convert("RGB")
    x = tfm(img).unsqueeze(0)  # (1,3,H,W)
    with torch.no_grad():
        out = model(x)
        prob = torch.softmax(out, dim=1)[0]
        idx = int(prob.argmax().item())
        conf = float(prob[idx].item())
        label = class_names[idx]

    # optional: low confidence = uncertain
    decision = "ok"
    if conf < 0.55:
        decision = "uncertain"

    return label, conf, decision

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", classes=class_names)

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file field"}), 400

    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        img = Image.open(f.stream)
        label, conf, decision = predict_pil(img)
        return jsonify({"label": label, "confidence": conf, "decision": decision})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
