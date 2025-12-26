import sys
import os

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# 🔹 IMPORTANT:
# Idhu class order. Train pannumbodhu train.py la print aayirukkum:
#   Classes: ['ai', 'real']  or ['real', 'ai']
# Andha order-ku EXACT-aa match aaganum.
CLASS_NAMES = ["ai", "real"]


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_transform():
    """Eval (val/test) time-la use pannara same transform."""
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
    """
    Architecture same as train.py:
    - ResNet-50 backbone
    - Last FC layer num_classes output
    Ippo weights=None use panrom (pretrained=False-ku badhila)
    so deprecated warning varadhu. Namma namma own weights load pannuvom.
    """
    model = models.resnet50(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model


def load_model(weights_path, device):
    """train.py save pannina .pth weights load pannradhu."""
    model = build_model()
    state = torch.load(weights_path, map_location=device)
    model.load_state_dict(state)
    model.to(device)
    model.eval()
    return model


def predict_image(image_path, model, device):
    """Single image-ku label + confidence return pannum."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    transform = get_transform()

    # Image open pannradhu
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0).to(device)  # [1, C, H, W]

    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        pred_idx = torch.argmax(probs).item()
        pred_label = CLASS_NAMES[pred_idx]
        pred_conf = probs[pred_idx].item()

    return pred_label, pred_conf


def main():
    if len(sys.argv) < 2:
        print("Use: python predict.py <path_to_image>")
        sys.exit(1)

    image_path = sys.argv[1]

    device = get_device()
    print(f"Using device: {device}")

    # train.py la save pannina weights path
    weights_path = os.path.join("models", "resnet50_ai_vs_real.pth")

    if not os.path.exists(weights_path):
        print(f"Model weights not found: {weights_path}")
        sys.exit(1)

    model = load_model(weights_path, device)

    label, conf = predict_image(image_path, model, device)
    print(f"\nPrediction: {label.upper()} (confidence: {conf:.2f})")

    if label == "ai":
        print("➡ This image is likely AI-generated.")
    else:
        print("➡ This image is likely a REAL camera photo.")


if __name__ == "__main__":
    main()
