"""
Component 2 Service - Dual Feature Service
===========================================
This service provides TWO different features based on issue type:

1. For ROAD issues: AI vs Real Image Detection (Port 5002)
   - Detects if image is AI-generated or real photo
   - Runs during validation (before submit)
   
2. For GARBAGE issues: Garbage Type Classification + Detailed Detection
   - Classifies garbage type (plastic, organic, metal, etc.)
   - Calls detailed garbage identification service (Port 5003)
   - Shows ALL detected garbage types in terminal
   - Runs IMMEDIATELY when user selects image (auto-fills field)

Architecture:
- AI Detection Service: http://localhost:5002/analyze
- Garbage Classification Service: http://localhost:5002/classify
- Detailed Garbage Identification: http://localhost:5003/predict (terminal output)
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import base64
import os
import sys
import requests

# Component directory
COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============= AI vs Real Detection Setup =============
def find_ai_model():
    """Find the AI vs Real model in multiple potential locations"""
    potential_rel_paths = [
        # Strategy 1: Double nested in voiceup folder (standard)
        os.path.join("voiceup-ai-or-real-image-classification-main", "voiceup-ai-or-real-image-classification-main", "models", "resnet50_ai_vs_real.pth"),
        # Strategy 2: Single nested
        os.path.join("voiceup-ai-or-real-image-classification-main", "models", "resnet50_ai_vs_real.pth"),
        # Strategy 3: Directly in models
        os.path.join("models", "resnet50_ai_vs_real.pth"),
    ]
    
    # Start from COMPONENT_DIR and go up to find the base 'component_vithushana' folder
    current = COMPONENT_DIR
    for _ in range(5):  # Go up to 5 levels to find the model
        for rel_path in potential_rel_paths:
            probe_path = os.path.abspath(os.path.join(current, rel_path))
            if os.path.exists(probe_path):
                print(f"🎯 AI Model found at: {probe_path}")
                return probe_path
        
        # Also try sibling folders if we are in a nested component folder
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
        
    # Final fallback: Hardcoded path based on project structure
    return os.path.join(COMPONENT_DIR, "..", "..", "voiceup-ai-or-real-image-classification-main", "voiceup-ai-or-real-image-classification-main", "models", "resnet50_ai_vs_real.pth")


AI_MODEL_PATH = find_ai_model()
AI_CLASS_NAMES = ["ai", "real"]

# ============= Garbage Classification Setup =============
GARBAGE_MODEL_PATH = os.path.join(COMPONENT_DIR, "garbage_model.pth")

app = Flask(__name__)
CORS(app)

# Global models
ai_model = None
ai_device = None
AI_MODEL_LOADED = False

garbage_model = None
garbage_class_names = []
GARBAGE_MODEL_LOADED = False


# ============= AI Detection Functions =============
def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_ai_transform():
    return transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])


def build_ai_model():
    model = models.resnet50(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, len(AI_CLASS_NAMES))
    return model


def load_ai_model():
    global ai_model, ai_device, AI_MODEL_LOADED
    try:
        ai_device = get_device()
        print(f"🔧 AI Detection - Using device: {ai_device}")
        
        if not os.path.exists(AI_MODEL_PATH):
            print(f"⚠️ AI model not found: {AI_MODEL_PATH}")
            return
        
        ai_model = build_ai_model()
        state = torch.load(AI_MODEL_PATH, map_location=ai_device)
        ai_model.load_state_dict(state)
        ai_model.to(ai_device)
        ai_model.eval()
        AI_MODEL_LOADED = True
        print("✅ AI vs Real model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load AI model: {e}")
        AI_MODEL_LOADED = False


def predict_ai_from_base64(image_data):
    """Predict if image is AI-generated or real"""
    try:
        # Remove data URI prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Transform and predict
        transform = get_ai_transform()
        tensor = transform(image).unsqueeze(0).to(ai_device)
        
        with torch.no_grad():
            outputs = ai_model(tensor)
            probs = torch.softmax(outputs, dim=1)[0]
            pred_idx = torch.argmax(probs).item()
            pred_label = AI_CLASS_NAMES[pred_idx]
            pred_conf = probs[pred_idx].item()
        
        return pred_label, pred_conf
    except Exception as e:
        raise Exception(f"AI prediction error: {str(e)}")


# ============= Garbage Classification Functions =============
def get_garbage_transform(img_size):
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
    ])


def load_garbage_model():
    global garbage_model, garbage_class_names, GARBAGE_MODEL_LOADED
    try:
        print(f"🔧 Loading garbage classification model...")
        
        if not os.path.exists(GARBAGE_MODEL_PATH):
            print(f"⚠️ Garbage model not found: {GARBAGE_MODEL_PATH}")
            return
        
        # Load checkpoint
        ckpt = torch.load(GARBAGE_MODEL_PATH, map_location="cpu")
        garbage_class_names = ckpt["class_names"]
        img_size = ckpt.get("img_size", 160)
        
        # Build model
        garbage_model = models.mobilenet_v2(weights=None)
        garbage_model.classifier[1] = nn.Linear(
            garbage_model.classifier[1].in_features,
            len(garbage_class_names)
        )
        garbage_model.load_state_dict(ckpt["model_state"])
        garbage_model.eval()
        
        GARBAGE_MODEL_LOADED = True
        print(f"✅ Garbage classification model loaded successfully")
        print(f"   Classes: {garbage_class_names}")
    except Exception as e:
        print(f"❌ Failed to load garbage model: {e}")
        GARBAGE_MODEL_LOADED = False


def predict_garbage_from_base64(image_data):
    """Classify garbage type from image"""
    try:
        # Remove data URI prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Transform and predict
        img_size = 160  # Default from training
        transform = get_garbage_transform(img_size)
        tensor = transform(image).unsqueeze(0)
        
        with torch.no_grad():
            outputs = garbage_model(tensor)
            probs = torch.softmax(outputs, dim=1)[0]
            pred_idx = torch.argmax(probs).item()
            pred_label = garbage_class_names[pred_idx]
            pred_conf = probs[pred_idx].item()
        
        # Determine if prediction is confident
        is_confident = pred_conf >= 0.55
        
        return pred_label, pred_conf, is_confident
    except Exception as e:
        raise Exception(f"Garbage classification error: {str(e)}")


# ============= NEW: Detailed Garbage Identification Function =============
def detect_garbage_types_terminal(image_data: str):
    """
    Call the detailed garbage identification service (port 5003)
    Shows ALL detected garbage types in terminal
    Returns the best match label from Port 5003, or None if unavailable
    """
    try:
        print(f"\n{'='*50}")
        print(f"🗑️ DETAILED GARBAGE TYPE DETECTION")
        print(f"{'='*50}")
        print(f"📡 Calling Garbage Identification Service (Port 5003)...")
        
        response = requests.post(
            'http://localhost:5003/predict',
            json={'image': image_data},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            detections = result.get('detections', [])
            best_prediction = result.get('best_prediction')
            
            print(f"✅ Garbage detection completed!")
            print(f"📊 Found {len(detections)} garbage items:")
            
            if detections:
                for i, detection in enumerate(detections, 1):
                    class_name = detection.get('class_name', 'Unknown')
                    confidence = detection.get('confidence', 0)
                    print(f"   {i}. {class_name} (Confidence: {confidence:.2f})")
                
                if best_prediction:
                    best_name = best_prediction.get('class_name', 'Unknown')
                    best_conf = best_prediction.get('confidence', 0)
                    print(f"\n🎯 BEST MATCH: {best_name} (Confidence: {best_conf:.2f})")
                    print(f"{'='*50}\n")
                    return best_name.lower(), best_conf
            else:
                print(f"   No garbage detected in image")
                
        else:
            print(f"❌ Garbage detection service error: {response.status_code}")
            
        print(f"{'='*50}\n")
        return None, None
        
    except Exception as e:
        print(f"❌ Error calling garbage detection: {e}")
        print(f"{'='*50}\n")
        return None, None


# Load both models on startup
load_ai_model()
load_garbage_model()


# ============= API Endpoints =============

@app.route('/')
def home():
    """Demo page for testing the service"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'component': 'Component 2 - Dual Service',
        'ai_detection_loaded': AI_MODEL_LOADED,
        'garbage_classification_loaded': GARBAGE_MODEL_LOADED,
        'version': '2.1'
    })


@app.route('/analyze', methods=['POST'])
def analyze_ai():
    """
    AI vs Real Image Detection (for ROAD issues)
    
    This endpoint is called during validation (before submit)
    Only for issue_type == 'road'
    """
    try:
        if not AI_MODEL_LOADED:
            print(f"\n⚠️ AI model not loaded - returning fallback PASS for road issue")
            return jsonify({
                'flutter_response': {
                    'success': True,
                    'can_proceed': True,
                    'title': '✅ Image Accepted',
                    'message': 'Image verification passed (model unavailable - fallback mode)',
                    'status_code': 'APPROVED'
                },
                'final_decision': {
                    'status': 'ACCEPTED',
                    'accepted': True,
                    'strike_issued': False
                }
            }), 200
        
        data = request.get_json()
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        print(f"\n🤖 AI DETECTION REQUEST (Road Issue)")
        
        # Run AI detection
        label, confidence = predict_ai_from_base64(image_data)
        is_ai_generated = (label == 'ai')
        
        print(f"   Result: {label.upper()} ({confidence:.2%})")
        
        # Create response
        if is_ai_generated:
            result = {
                'flutter_response': {
                    'success': False,
                    'can_proceed': False,
                    'title': '🤖 AI-Generated Image Detected',
                    'message': 'Your image appears to be AI-generated',
                    'detailed_explanation': f'Our AI detection system has determined that this image is likely generated by artificial intelligence (confidence: {confidence:.1%}). For authenticity, we only accept real photographs.',
                    'what_to_do_next': 'Please take a real photograph using your camera.',
                    'status_code': 'REJECTED'
                },
                'final_decision': {
                    'status': 'REJECTED - AI GENERATED IMAGE',
                    'accepted': False,
                    'strike_issued': False
                },
                'simple_notification': {
                    'title': '🤖 AI-Generated Image',
                    'message': 'Your post was rejected because the image appears to be AI-generated.',
                    'type': 'warning'
                }
            }
        else:
            result = {
                'flutter_response': {
                    'success': True,
                    'can_proceed': True,
                    'title': '✅ Real Image Verified',
                    'message': 'Your image is a real photograph',
                    'status_code': 'APPROVED'
                },
                'final_decision': {
                    'status': 'ACCEPTED',
                    'accepted': True,
                    'strike_issued': False
                }
            }
        
        return jsonify(result), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/classify', methods=['POST'])
def classify_garbage():
    """
    Garbage Type Classification (for GARBAGE issues)
    
    This endpoint is called IMMEDIATELY when user selects image
    Returns garbage type to auto-fill the field
    Only for issue_type == 'garbage'
    
    NEW: Also calls detailed garbage detection (Port 5003) for terminal output
    """
    try:
        if not GARBAGE_MODEL_LOADED:
            print(f"\n⚠️ Garbage model not loaded - returning fallback response")
            return jsonify({
                'success': True,
                'garbage_type': 'general waste',
                'confidence': 0.5,
                'confidence_percent': '50.00%',
                'is_confident': True,
                'all_classes': ['general waste'],
                'message': 'Detected: general waste (fallback mode - model unavailable)'
            }), 200
        
        data = request.get_json()
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        print(f"\n🗑️ GARBAGE CLASSIFICATION REQUEST")
        
        # Run garbage classification
        label, confidence, is_confident = predict_garbage_from_base64(image_data)
        
        print(f"   Result: {label} ({confidence:.2%}) - {'Confident' if is_confident else 'Uncertain'}")
        
        # Call detailed garbage detection (Port 5003) and use its result if available
        print(f"   📡 Calling detailed garbage identification...")
        detailed_label, detailed_conf = detect_garbage_types_terminal(image_data)
        
        # Use Port 5003 result if available (higher accuracy YOLO model)
        final_label = detailed_label if detailed_label else label
        final_confidence = detailed_conf if detailed_conf else confidence
        final_confident = final_confidence >= 0.55
        
        # Return classification result
        result = {
            'success': True,
            'garbage_type': final_label,
            'confidence': round(final_confidence, 4),
            'confidence_percent': f"{final_confidence * 100:.2f}%",
            'is_confident': final_confident,
            'all_classes': garbage_class_names,
            'message': f"Detected: {final_label}" if final_confident else f"Uncertain: {final_label} (low confidence)"
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING COMPONENT 2 - DUAL SERVICE")
    print("="*60)
    print(f"Component: AI Detection + Garbage Classification")
    print(f"Port: 5002")
    print(f"")
    print(f"Endpoints:")
    print(f"  - GET  /health          (Health check)")
    print(f"  - POST /analyze         (AI vs Real - for ROAD issues)")
    print(f"  - POST /classify        (Garbage Type - for GARBAGE issues)")
    print(f"")
    print(f"Integration:")
    print(f"  - Detailed Garbage Detection: http://localhost:5003/predict")
    print(f"  - Terminal Output: All garbage types detected")
    print(f"")
    print(f"Models:")
    print(f"  - AI Detection: {'✅ Loaded' if AI_MODEL_LOADED else '❌ Not Loaded'}")
    print(f"  - Garbage Classification: {'✅ Loaded' if GARBAGE_MODEL_LOADED else '❌ Not Loaded'}")
    if GARBAGE_MODEL_LOADED:
        print(f"  - Garbage Classes: {garbage_class_names}")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=True,
        use_reloader=False
    )