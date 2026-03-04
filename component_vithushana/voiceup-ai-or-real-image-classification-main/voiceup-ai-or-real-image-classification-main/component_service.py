"""
Component 2 Service - AI vs Real Image Detection
=================================================
This runs the AI-generated vs Real image classifier as a separate service on port 5002.
The main application backend calls this service via HTTP.

Model: ResNet50 trained to detect AI-generated images
Classes: ['ai', 'real']
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import base64
import os
import sys

# Add current directory to path
COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, COMPONENT_DIR)

# Configuration
CLASS_NAMES = ["ai", "real"]
MODEL_WEIGHTS_PATH = os.path.join(COMPONENT_DIR, "models", "resnet50_ai_vs_real.pth")

app = Flask(__name__)
CORS(app)

# Global model variable
model = None
device = None
COMPONENT_LOADED = False


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


def predict_from_base64(image_data, model, device):
    """
    Predict from base64 encoded image
    
    Args:
        image_data: Base64 encoded image (with or without data URI prefix)
        model: Loaded PyTorch model
        device: torch device
    
    Returns:
        (label, confidence) tuple
    """
    try:
        # Remove data URI prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Transform and predict
        transform = get_transform()
        tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = model(tensor)
            probs = torch.softmax(outputs, dim=1)[0]
            pred_idx = torch.argmax(probs).item()
            pred_label = CLASS_NAMES[pred_idx]
            pred_conf = probs[pred_idx].item()
        
        return pred_label, pred_conf
    
    except Exception as e:
        raise Exception(f"Prediction error: {str(e)}")


# Load model on startup
try:
    device = get_device()
    print(f"🔧 Using device: {device}")
    
    model = load_model(MODEL_WEIGHTS_PATH, device)
    COMPONENT_LOADED = True
    print("✅ AI vs Real model loaded successfully")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    COMPONENT_LOADED = False


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'component': 'AI vs Real Image Classifier',
        'loaded': COMPONENT_LOADED,
        'version': '1.0'
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint
    
    Request body:
    {
        "image": "base64_encoded_image",
        "description": "text description" (optional, not used),
        "issue_type": "road" or "garbage" (optional, not used)
    }
    
    Returns:
    {
        "flutter_response": { ... },
        "final_decision": { ... },
        "simple_notification": { ... },
        "ai_detection": { ... }
    }
    """
    try:
        if not COMPONENT_LOADED:
            return jsonify({
                'flutter_response': {
                    'success': False,
                    'can_proceed': False,
                    'title': '❌ AI Detector Not Loaded',
                    'message': 'The AI detection model failed to load',
                    'detailed_explanation': 'The AI vs Real image classifier could not be initialized.',
                    'what_to_do_next': 'Contact support to restart the AI detection service.',
                    'status_code': 'ERROR',
                    'component_name': 'AI Image Detection',
                    'component_number': 2,
                    'total_components': 4
                },
                'final_decision': {
                    'status': 'ERROR',
                    'accepted': False,
                    'reason': 'AI detector not loaded',
                    'strike_issued': False
                },
                'simple_notification': {
                    'title': '❌ System Error',
                    'message': 'AI detection service is unavailable.',
                    'type': 'error'
                }
            }), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        print(f"\n{'='*60}")
        print(f"🤖 AI DETECTION REQUEST")
        print(f"{'='*60}")
        print(f"Image Data Length: {len(image_data)} characters")
        print(f"{'='*60}\n")
        
        # Run AI detection
        label, confidence = predict_from_base64(image_data, model, device)
        
        print(f"🔍 Prediction: {label.upper()} ({confidence:.2%})")
        
        # Determine if image is accepted
        is_ai_generated = (label == 'ai')
        
        # Create response based on result
        if is_ai_generated:
            # AI-generated image - REJECT
            result = {
                'flutter_response': {
                    'success': False,
                    'can_proceed': False,
                    'title': '🤖 AI-Generated Image Detected',
                    'message': 'Your image appears to be AI-generated',
                    'detailed_explanation': f'Our AI detection system has determined that this image is likely generated by artificial intelligence (confidence: {confidence:.1%}). For authenticity and verification purposes, we only accept real photographs taken with a camera. AI-generated images cannot be used to report real-world issues.',
                    'what_to_do_next': 'Please take a real photograph of the issue using your camera and submit again. Make sure to capture the actual problem location with your device\'s camera.',
                    'status_code': 'REJECTED',
                    'component_name': 'AI Image Detection',
                    'component_number': 2,
                    'total_components': 4
                },
                'final_decision': {
                    'status': 'REJECTED - AI GENERATED IMAGE',
                    'accepted': False,
                    'reason': f'Image detected as AI-generated (confidence: {confidence:.1%})',
                    'strike_issued': False
                },
                'simple_notification': {
                    'title': '🤖 AI-Generated Image',
                    'message': f'Your post was rejected because the image appears to be AI-generated. Please use a real camera photo.',
                    'type': 'warning'
                },
                'ai_detection': {
                    'is_ai_generated': True,
                    'label': label,
                    'confidence': round(confidence, 4),
                    'confidence_percent': f"{confidence * 100:.2f}%"
                }
            }
        else:
            # Real image - ACCEPT
            result = {
                'flutter_response': {
                    'success': True,
                    'can_proceed': True,
                    'title': '✅ Real Image Verified',
                    'message': 'Your image is a real photograph',
                    'detailed_explanation': f'Our AI detection system has verified that this is a real photograph (confidence: {confidence:.1%}).',
                    'what_to_do_next': 'Your image has passed AI detection. Continue with submission.',
                    'status_code': 'APPROVED',
                    'component_name': 'AI Image Detection',
                    'component_number': 2,
                    'total_components': 4
                },
                'final_decision': {
                    'status': 'ACCEPTED',
                    'accepted': True,
                    'reason': f'Image verified as real photograph (confidence: {confidence:.1%})',
                    'strike_issued': False
                },
                'simple_notification': {
                    'title': '✅ Real Image',
                    'message': 'Your image has been verified as a real photograph.',
                    'type': 'success'
                },
                'ai_detection': {
                    'is_ai_generated': False,
                    'label': label,
                    'confidence': round(confidence, 4),
                    'confidence_percent': f"{confidence * 100:.2f}%"
                }
            }
        
        print(f"\n{'='*60}")
        print(f"📤 AI DETECTION RESULT")
        print(f"{'='*60}")
        print(f"Label: {label.upper()}")
        print(f"Confidence: {confidence:.2%}")
        print(f"Accepted: {not is_ai_generated}")
        print(f"{'='*60}\n")
        
        return jsonify(result), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'flutter_response': {
                'success': False,
                'can_proceed': False,
                'title': '❌ AI Detection Error',
                'message': 'An error occurred during AI detection',
                'detailed_explanation': f'Error: {str(e)}',
                'what_to_do_next': 'Please try again. If the problem persists, contact support.',
                'status_code': 'ERROR',
                'component_name': 'AI Image Detection',
                'component_number': 2,
                'total_components': 4
            },
            'final_decision': {
                'status': 'ERROR',
                'accepted': False,
                'reason': str(e),
                'strike_issued': False
            },
            'simple_notification': {
                'title': '❌ Error',
                'message': 'An error occurred during AI detection. Please try again.',
                'type': 'error'
            }
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING COMPONENT 2 SERVICE - OLD VERSION (DEPRECATED)")
    print("="*60)
    print(f"Component: AI vs Real Image Classifier")
    print(f"Model: ResNet50")
    print(f"Port: 5099 (Changed from 5002 to avoid conflict)")
    print(f"Note: This is the OLD standalone service. Use run_component_2.py instead!")
    print(f"Endpoints:")
    print(f"  - GET  /health  (Health check)")
    print(f"  - POST /analyze (AI Detection)")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5099,
        debug=True
    )
