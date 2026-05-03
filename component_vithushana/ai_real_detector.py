"""
Component 2: AI vs Real Image Detection
Detects whether an image is AI-generated or a real camera photo
"""

import os
import base64
import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

# Model configuration
CLASS_NAMES = ["ai", "real"]
MODEL_WEIGHTS_PATH = os.path.join(
    os.path.dirname(__file__),
    "voiceup-ai-or-real-image-classification-main",
    "voiceup-ai-or-real-image-classification-main",
    "models",
    "resnet50_ai_vs_real.pth"
)

# Global model instance
ai_real_model = None
device = None


def get_device():
    """Get compute device (GPU if available, else CPU)"""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def get_transform():
    """Image preprocessing transforms"""
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
    """Build ResNet-50 model architecture"""
    model = models.resnet50(weights=None)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model


def load_ai_real_model():
    """Load the AI vs Real detection model (called once at startup)"""
    global ai_real_model, device
    
    if ai_real_model is not None:
        return ai_real_model
    
    try:
        device = get_device()
        print(f"🤖 Loading AI vs Real Detection Model...")
        print(f"   Device: {device}")
        print(f"   Model path: {MODEL_WEIGHTS_PATH}")
        
        if not os.path.exists(MODEL_WEIGHTS_PATH):
            print(f"⚠️  Model weights not found at: {MODEL_WEIGHTS_PATH}")
            print(f"   Component 2 will be disabled")
            return None
        
        model = build_model()
        state = torch.load(MODEL_WEIGHTS_PATH, map_location=device)
        model.load_state_dict(state)
        model.to(device)
        model.eval()
        
        ai_real_model = model
        print(f"✅ AI vs Real Detection Model loaded successfully")
        return model
    
    except Exception as e:
        print(f"❌ Failed to load AI vs Real model: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def predict_from_base64(image_data: str) -> tuple:
    """
    Predict if image is AI-generated or real from base64 string
    
    Args:
        image_data: Base64 encoded image string
    
    Returns:
        tuple: (label, confidence) where label is 'ai' or 'real'
    """
    global ai_real_model, device
    
    if ai_real_model is None:
        raise Exception("AI vs Real model not loaded")
    
    try:
        # Decode base64 to image
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Transform and predict
        transform = get_transform()
        tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            outputs = ai_real_model(tensor)
            probs = torch.softmax(outputs, dim=1)[0]
            pred_idx = torch.argmax(probs).item()
            pred_label = CLASS_NAMES[pred_idx]
            pred_conf = probs[pred_idx].item()
        
        return pred_label, pred_conf
    
    except Exception as e:
        raise Exception(f"AI vs Real prediction error: {str(e)}")


def analyze_image_authenticity(image_data: str, description: str = "", issue_type: str = "road") -> dict:
    """
    Main function to analyze if image is AI-generated or real
    ONLY FOR ROAD ISSUES - Garbage issues skip this check
    
    Args:
        image_data: Base64 encoded image
        description: Text description (currently not used)
        issue_type: 'road' or 'garbage' (only runs for 'road')
    
    Returns:
        dict with detection results and user-friendly messages
    """
    print("\n" + "="*60)
    print("🔍 Component 2: AI vs Real Image Detection")
    print("="*60)
    
    # Skip AI detection for garbage issues
    if issue_type.lower() == 'garbage':
        print("⏭️  Skipping AI detection for garbage issue (not applicable)")
        return {
            'final_decision': {
                'status': 'PASSED',
                'accepted': True,
                'reason': 'AI detection skipped for garbage issue',
                'strike_issued': False
            },
            'ai_detection': {
                'available': False,
                'label': 'skipped',
                'confidence': 0.0,
                'skipped_reason': 'Not applicable for garbage issues'
            },
            'flutter_response': {
                'success': True,
                'can_proceed': True,
                'title': 'AI Detection Skipped',
                'message': 'AI detection not required for garbage issues',
                'detailed_explanation': 'AI vs Real detection only applies to road issue reporting.',
                'what_to_do_next': 'Your garbage report is being processed.'
            }
        }
    
    try:
        # Check if model is loaded
        if ai_real_model is None:
            print("⚠️  AI vs Real model not available")
            return {
                'final_decision': {
                    'status': 'PASSED',
                    'accepted': True,
                    'reason': 'AI detection unavailable - skipped',
                    'strike_issued': False
                },
                'ai_detection': {
                    'available': False,
                    'label': 'unknown',
                    'confidence': 0.0
                },
                'flutter_response': {
                    'success': True,
                    'can_proceed': True,
                    'title': 'Image Check Skipped',
                    'message': 'AI detection model unavailable',
                    'detailed_explanation': 'The AI detection component is not available. Your post will proceed without this check.',
                    'what_to_do_next': 'Your post is being processed normally.'
                }
            }
        
        # Predict
        label, confidence = predict_from_base64(image_data)
        
        print(f"🤖 AI Detection Result: {label.upper()} (confidence: {confidence:.2%})")
        
        # Determine if AI-generated
        is_ai_generated = (label == "ai")
        
        if is_ai_generated:
            # REJECT - AI-generated image detected
            print(f"🚫 Decision: REJECTED - AI-generated image detected")
            
            return {
                'final_decision': {
                    'status': 'REJECTED - AI GENERATED',
                    'accepted': False,
                    'reason': f'AI-generated image detected (confidence: {confidence:.0%})',
                    'strike_issued': False  # No strike for AI images, just rejection
                },
                'ai_detection': {
                    'available': True,
                    'label': label,
                    'confidence': round(confidence, 4),
                    'is_ai_generated': True
                },
                'flutter_response': {
                    'success': False,
                    'can_proceed': False,
                    'title': 'AI-Generated Image Detected',
                    'message': 'Your image appears to be AI-generated, not a real photo.',
                    'detailed_explanation': f'Our AI detection system has identified this image as artificially generated with {confidence:.0%} confidence. VoiceUp only accepts real photographs taken by users to ensure authentic reporting of issues.',
                    'what_to_do_next': 'Please submit a real photograph taken with your camera. AI-generated, edited, or synthetic images are not accepted for issue reporting.',
                    'can_continue': False
                }
            }
        else:
            # PASS - Real image
            print(f"✅ Decision: PASSED - Real image confirmed")
            
            return {
                'final_decision': {
                    'status': 'PASSED',
                    'accepted': True,
                    'reason': f'Real image confirmed (confidence: {confidence:.0%})',
                    'strike_issued': False
                },
                'ai_detection': {
                    'available': True,
                    'label': label,
                    'confidence': round(confidence, 4),
                    'is_ai_generated': False
                },
                'flutter_response': {
                    'success': True,
                    'can_proceed': True,
                    'title': 'Image Verified',
                    'message': 'Real photograph confirmed',
                    'detailed_explanation': f'Your image has been verified as a real photograph with {confidence:.0%} confidence.',
                    'what_to_do_next': 'Your image has passed authenticity verification.'
                }
            }
    
    except Exception as e:
        print(f"❌ Error in AI vs Real detection: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # On error, allow to proceed (fail-open)
        return {
            'final_decision': {
                'status': 'ERROR',
                'accepted': True,  # Fail-open: allow on error
                'reason': f'AI detection error: {str(e)}',
                'strike_issued': False
            },
            'ai_detection': {
                'available': False,
                'error': str(e)
            },
            'flutter_response': {
                'success': True,
                'can_proceed': True,
                'title': 'Detection Error',
                'message': 'Unable to verify image authenticity',
                'detailed_explanation': 'There was an error checking if the image is AI-generated. Your post will proceed.',
                'what_to_do_next': 'Your post is being processed.'
            }
        }


# Load model at module import
print("🚀 Initializing Component 2: AI vs Real Detection...")
load_ai_real_model()
