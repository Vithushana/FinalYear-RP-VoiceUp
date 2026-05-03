"""
Garbage Type Classification
Real-time garbage type detection for auto-filling garbage type field
"""

import os
import base64
import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# Model configuration
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "Garbage_Classification-main",
    "Garbage_Classification-main",
    "garbage_model.pth"
)

# Global model instance
garbage_classifier_model = None
class_names = []
IMG_SIZE = 160


def load_garbage_classifier():
    """Load the garbage classification model (called once at startup)"""
    global garbage_classifier_model, class_names, IMG_SIZE
    
    if garbage_classifier_model is not None:
        return garbage_classifier_model
    
    try:
        print(f"🗑️  Loading Garbage Type Classification Model...")
        print(f"   Model path: {MODEL_PATH}")
        
        if not os.path.exists(MODEL_PATH):
            print(f"⚠️  Garbage model not found at: {MODEL_PATH}")
            print(f"   Garbage classification will be disabled")
            return None
        
        # Load checkpoint
        ckpt = torch.load(MODEL_PATH, map_location="cpu")
        class_names = ckpt["class_names"]
        IMG_SIZE = ckpt.get("img_size", 160)
        
        # Build model architecture
        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(class_names))
        model.load_state_dict(ckpt["model_state"])
        model.eval()
        
        garbage_classifier_model = model
        print(f"✅ Garbage Classification Model loaded successfully")
        print(f"   Classes: {class_names}")
        return model
    
    except Exception as e:
        print(f"❌ Failed to load Garbage Classification model: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def classify_garbage_from_base64(image_data: str) -> tuple:
    """
    Classify garbage type from base64 image string
    
    Args:
        image_data: Base64 encoded image string
    
    Returns:
        tuple: (label, confidence, decision) 
        - label: garbage type (e.g., 'plastic', 'metal', 'paper')
        - confidence: 0.0-1.0
        - decision: 'ok' or 'uncertain' (if confidence < 0.55)
    """
    global garbage_classifier_model, class_names, IMG_SIZE
    
    if garbage_classifier_model is None:
        raise Exception("Garbage classification model not loaded")
    
    try:
        # Decode base64 to image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Transform and predict
        tfm = transforms.Compose([
            transforms.Resize((IMG_SIZE, IMG_SIZE)),
            transforms.ToTensor(),
        ])
        
        x = tfm(image).unsqueeze(0)  # (1,3,H,W)
        
        with torch.no_grad():
            out = garbage_classifier_model(x)
            prob = torch.softmax(out, dim=1)[0]
            idx = int(prob.argmax().item())
            conf = float(prob[idx].item())
            label = class_names[idx]
        
        # Low confidence = uncertain
        decision = "ok" if conf >= 0.55 else "uncertain"
        
        return label, conf, decision
    
    except Exception as e:
        raise Exception(f"Garbage classification error: {str(e)}")


def detect_garbage_type(image_data: str) -> dict:
    """
    Detect garbage type for real-time auto-fill in Flutter app
    
    Args:
        image_data: Base64 encoded image
    
    Returns:
        dict with garbage type, confidence, and user message
    """
    print("\n" + "="*60)
    print("🗑️  Real-time Garbage Type Detection")
    print("="*60)
    
    try:
        # Check if model is loaded
        if garbage_classifier_model is None:
            print("⚠️  Garbage classification model not available")
            return {
                'success': False,
                'available': False,
                'garbage_type': 'Unknown',
                'confidence': 0.0,
                'message': 'Garbage classification unavailable'
            }
        
        # Classify
        label, confidence, decision = classify_garbage_from_base64(image_data)
        
        print(f"🗑️  Detected: {label.upper()} (confidence: {confidence:.2%}, {decision})")
        
        # Format label for display (capitalize)
        formatted_label = label.capitalize()
        
        return {
            'success': True,
            'available': True,
            'garbage_type': formatted_label,
            'confidence': round(confidence, 4),
            'decision': decision,
            'message': f"Detected: {formatted_label}" if decision == 'ok' else f"Uncertain: {formatted_label}"
        }
    
    except Exception as e:
        print(f"❌ Error in garbage classification: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'success': False,
            'available': False,
            'error': str(e),
            'garbage_type': 'Unknown',
            'confidence': 0.0,
            'message': 'Error detecting garbage type'
        }


# Load model at module import
print("🚀 Initializing Garbage Type Classification...")
load_garbage_classifier()
