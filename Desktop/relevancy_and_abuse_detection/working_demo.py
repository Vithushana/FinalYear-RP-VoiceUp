"""
QUICK FIX WEB APP - WORKING VERSION
==================================
Simple web app that works immediately for your demo
"""

# Load environment variables from .env file (for DistilBERT API key)
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load DISTILBERT_API_KEY from .env file
except ImportError:
    pass  # dotenv not installed, will use system environment variables

from flask import Flask, render_template_string, request, jsonify
import os
import cv2
import numpy as np
import pickle
import base64
import io
from datetime import datetime
import traceback
from emergency_road_detector import EmergencyRoadDetector
from ultralytics import YOLO
import torch
from enhanced_road_detection import EnhancedRoadDetectionSystem
try:
    from distilbert_abuse_detector import analyze_text_abuse, get_distilbert_pipeline
    DISTILBERT_AVAILABLE = True
    print("✅ DistilBERT Abuse Detection Module imported successfully")
except ImportError:
    print("⚠️ DistilBERT module not found. Text AI model will be disabled.")
    DISTILBERT_AVAILABLE = False

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# LOAD TRAINED YOLO MODELS
print("🚀 Loading trained AI models...")

# Initialize model variables
enhanced_road_detector = None
abuse_model = None
enhanced_road_detector = None
abuse_model = None
privacy_model = None
distilbert_pipeline = None

# Update model loading to use available fallback models
road_models = []

# Load fallback road models
fallback_model_paths = [
    "models/road_detection_ultimate/training/weights/best.pt",
    "models/road_detection_model.pt"
]

for model_path in fallback_model_paths:
    if os.path.exists(model_path):
        model = YOLO(model_path)
        road_models.append(model)
        print(f"✅ Loaded road model: {model_path}")
    else:
        print(f"❌ Road model not found: {model_path}")

print(f"📊 Road Detection Status: {len(road_models)}/{len(fallback_model_paths)} models loaded")

try:
    # Load enhanced road detection system (combines both VSC and Colab models)
    enhanced_road_detector = EnhancedRoadDetectionSystem()
    print("✅ Enhanced road detection system loaded (VSC + Colab models)")
except Exception as e:
    print(f"⚠️ Error loading enhanced road detection system: {e}")
    enhanced_road_detector = None

try:
    # Load your TRAINED abuse detection model (96.5% mAP50, 69 epochs)
    abuse_model_path = "models/abuse_detection_final/abuse_detection_best.pt"
    if os.path.exists(abuse_model_path):
        abuse_model = YOLO(abuse_model_path)
        print("✅ TRAINED Abuse detection model loaded (96.5% mAP50)")
    else:
        # Fallback to older model
        fallback_path = "models/abusive_detection_ultimate/training/weights/best.pt"
        if os.path.exists(fallback_path):
            abuse_model = YOLO(fallback_path)
            print("✅ Fallback abuse detection model loaded")
        else:
            abuse_model = None
            print("⚠️ No abuse model found")
    
    # Load your TRAINED human detection model (90.6% mAP50)
    human_model_path = "models/human_detection_final/human_detection_best.pt"
    if os.path.exists(human_model_path):
        privacy_model = YOLO(human_model_path)
        print("✅ TRAINED Human detection model loaded (90.6% mAP50)")
    else:
        # Fallback to pre-trained
        try:
            privacy_model = YOLO('yolov8n.pt')  # Pre-trained model with person detection
            print("✅ Fallback human detection model loaded")
        except:
            privacy_model = None
            print("⚠️ No privacy model available")
        
    # Load Garbage Classification Model (100% accuracy)
    garbage_model_path = "garbage-results/best.pt"
    if os.path.exists(garbage_model_path):
        garbage_model = YOLO(garbage_model_path)
        print("✅ TRAINED Garbage classification model loaded (100% accuracy)")
    else:
        garbage_model = None
        print("⚠️ Garbage classification model not found")
        
except Exception as e:
    print(f"⚠️ Error loading models: {e}")
    road_model = None
    abuse_model = None
    garbage_model = None

# Load DistilBERT Abuse Detection Model
distilbert_pipeline = None
if DISTILBERT_AVAILABLE:
    try:
        print("🤖 Initializing DistilBERT Text Abuse Detection Model...")
        distilbert_pipeline = get_distilbert_pipeline("models/text_abuse_model")
        print("✅ DistilBERT Model (fine-tuned) loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading DistilBERT model: {e}")
        print("⚠️ Text abuse detection will use keyword filtering only.")

print("🎯 AI-Enhanced Detection System Ready!")

# PRIVACY PROTECTION: Human Detection Function
def detect_humans_for_privacy(image):
    """
    PRIVACY PROTECTION: Detect humans in road images
    Returns True if humans detected (reject for privacy), False if safe
    """
    global privacy_model
    
    if privacy_model is None:
        return False  # No privacy model available, proceed normally
    
    try:
        # Run human detection
        results = privacy_model(image, verbose=False)
        
        # Check for person detections (class 0 in COCO dataset)
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                classes = boxes.cls.cpu().numpy()
                confidences = boxes.conf.cpu().numpy()
                
                # Check for person detections with reasonable confidence
                for cls, conf, box in zip(classes, confidences, boxes.xyxy.cpu().numpy()):
                    # RELAXED THRESHOLD: 0.45 (was 0.55) to catch more people
                    if int(cls) == 0 and conf > 0.45:  
                        
                        # REALISM CHECK: Distinguish real humans from icons/cartoons
                        x1, y1, x2, y2 = map(int, box)
                        
                        # Ensure coordinates are within image bounds
                        h, w = image.shape[:2]
                        x1, y1 = max(0, x1), max(0, y1)
                        x2, y2 = min(w, x2), min(h, y2)
                        
                        # SIZE CHECK: Ignore tiny detections (often noise or far away bystanders)
                        box_area = (x2 - x1) * (y2 - y1)
                        image_area = h * w
                        if box_area / image_area < 0.01: # Less than 1% of image
                             print(f"⚠️ Privacy Check: Ignored tiny person detection ({box_area/image_area:.4f} of image)")
                             continue
                        
                        # Extract the person region
                        person_roi = image[y1:y2, x1:x2]
                        
                        if person_roi.size > 0:
                            # Convert to grayscale for texture analysis
                            roi_gray = cv2.cvtColor(person_roi, cv2.COLOR_BGR2GRAY)
                            
                            # 1. Texture Check (Laplacian Variance)
                            # Real photos have high texture variance (skin, clothes). Icons are flat.
                            laplacian_var = cv2.Laplacian(roi_gray, cv2.CV_64F).var()
                            
                            # 2. Color Complexity Check (Histogram)
                            # Real photos have complex color distributions. Icons have few colors.
                            hist = cv2.calcHist([roi_gray], [0], None, [256], [0, 256])
                            hist_norm = hist / (roi_gray.shape[0] * roi_gray.shape[1])
                            top_5_sum = np.sum(np.sort(hist_norm.flatten())[-5:])
                            
                            print(f"🔍 Privacy Debug: Person detected - Conf: {conf:.2f}, Texture: {laplacian_var:.1f}, Uniformity: {top_5_sum:.2f}")
                            
                            # Thresholds for "Realism"
                            # Icons: Low texture (< 10) OR High uniformity (> 0.60)
                            # Real Humans: High texture (> 10) AND Low uniformity (< 0.60)
                            
                            # CRITICAL FIX: Trust the model if confidence is high (> 0.60)
                            # OR if the image has complex colors (low uniformity) even if texture is low (blur/filter)
                            
                            is_fake = False
                            if top_5_sum > 0.60: # Extremely uniform (flat icon)
                                is_fake = True
                                print(f"⚠️ Privacy Check: Ignored - Too uniform ({top_5_sum:.2f})")
                            elif laplacian_var < 10 and conf < 0.60: # Very flat AND low confidence
                                is_fake = True
                                print(f"⚠️ Privacy Check: Ignored - Low texture & low conf")
                                
                            if is_fake:
                                print(f"⚠️ Privacy Check: Ignored non-realistic person (Icon/Cartoon)")
                                continue  # Skip this detection, it's likely an icon
                        
                        print(f"🛡️ Privacy Protection: Real human detected (confidence: {conf:.2f})")
                        return True
        
        return False  # No humans detected, safe for privacy
    
    except Exception as e:
        print(f"⚠️ Privacy detection error: {e}")
        return False  # If error, proceed normally

# HARISH'S COMPLETE TWO-PHASE FILTERATION SYSTEM
# Add detailed debugging for model predictions
STRICT_CONFIDENCE_THRESHOLD = 0.50  # Lowered threshold

# AI TEXT ANALYSIS HELPER
def analyze_text_with_ai(text):
    """
    Analyze text using the fine-tuned DistilBERT model
    Returns: (is_abusive, category, confidence)
    """
    global distilbert_pipeline
    
    if distilbert_pipeline is None:
        return False, None, 0.0
        
    try:
        # Use DistilBERT pipeline for inference (STRICT threshold for government platform)
        is_abusive, category, confidence = distilbert_pipeline.predict(text, threshold=0.50)
        
        print(f"🤖 DistilBERT Analysis: {category} (confidence: {confidence:.2%})")
        
        return is_abusive, category, confidence
        
    except Exception as e:
        print(f"⚠️ DistilBERT Analysis Error: {e}")
        return False, None, 0.0

# Update analyze_content to include fallback logic and debugging
def analyze_content(image_data, description):
    """
    Updated HARISH'S RELEVANCE AND ABUSE FILTERATION SYSTEM
    Combines predictions from all road models for better accuracy.
    """
    global road_models, abuse_model, enhanced_road_detector

    # Decode image (existing logic)
    try:
        print("🔍 Debug: analyze_content started")
        print(f"🔍 Debug: enhanced_road_detector is {'defined' if 'enhanced_road_detector' in globals() else 'NOT DEFINED'}")
        if 'enhanced_road_detector' in globals():
            print(f"🔍 Debug: enhanced_road_detector value: {enhanced_road_detector}")
        print(f"🔍 Debug: Received image_data type: {type(image_data)}")
        print(f"🔍 Debug: Image data length: {len(image_data) if image_data else 0}")
        
        # Validate input data
        if not image_data:
            raise ValueError("No image data received")
        
        if len(image_data) < 50:  # Too short to be valid base64 image
            raise ValueError("Image data too short - invalid format")
        
        # Extract base64 data with multiple methods
        base64_data = None
        
        if ',' in image_data:
            # Standard data URL format: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAA..."
            parts = image_data.split(',')
            if len(parts) >= 2:
                base64_data = parts[1]
                print(f"🔍 Debug: Extracted base64 from data URL, length: {len(base64_data)}")
            else:
                raise ValueError("Invalid data URL format")
        else:
            # Raw base64 data
            base64_data = image_data
            print(f"🔍 Debug: Using raw base64 data, length: {len(base64_data)}")
        
        # Clean base64 data
        base64_data = base64_data.strip()
        
        # Add padding if needed
        padding_needed = 4 - (len(base64_data) % 4)
        if padding_needed != 4:
            base64_data += '=' * padding_needed
            print(f"🔍 Debug: Added {padding_needed} padding characters")
        
        # Decode base64 to numpy array
        try:
            decoded_bytes = base64.b64decode(base64_data)
            print(f"🔍 Debug: Base64 decoded successfully, bytes length: {len(decoded_bytes)}")
        except Exception as b64_error:
            raise ValueError(f"Base64 decoding failed: {str(b64_error)}")
        
        if len(decoded_bytes) < 100:  # Too small to be a valid image
            raise ValueError("Decoded data too small - not a valid image")
        
        # Convert to numpy array
        nparr = np.frombuffer(decoded_bytes, np.uint8)
        print(f"🔍 Debug: Created numpy array, shape: {nparr.shape}")
        
        # Decode image with OpenCV
        img_color = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        print(f"🔍 Debug: OpenCV decode result: {img_color.shape if img_color is not None else 'None'}")
        
        # Check if image decoding was successful
        if img_color is None:
            # Try alternative decoding methods
            img_color = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            if img_color is not None and len(img_color.shape) == 3:
                print("🔍 Debug: Alternative decode method worked")
            else:
                raise ValueError("OpenCV failed to decode image - unsupported format or corrupted data")
        
        if img_color.size == 0:
            raise ValueError("Decoded image is empty")
        
        # Convert to grayscale
        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        
        # Check if conversion was successful
        if img_gray is None or img_gray.size == 0:
            raise ValueError("Failed to convert image to grayscale")
        
        height, width = img_gray.shape[:2]
        
        # Validate image dimensions
        if height <= 0 or width <= 0:
            raise ValueError(f"Invalid image dimensions: {width}x{height}")
            
    except Exception as img_error:
        print(f"🚨 Image decoding error: {img_error}")
        error_msg = str(img_error)
        if "decode" in error_msg.lower() or "valid image" in error_msg.lower():
            error_msg += " (Note: AVIF/HEIC formats are often not supported. Please use JPG/PNG)"
            
        return {
            'error': error_msg,
            'final_decision': {
                'status': 'ERROR',
                'accepted': False,
                'reason': 'Invalid image data - please upload a valid image file',
                'strike_issued': False,
                'system_type': 'ERROR HANDLER'
            }
        }
    
    # Basic image analysis (always calculate these for fallback and result display)
    avg_brightness = np.mean(img_gray)
    edges = cv2.Canny(img_gray, 50, 150)
    edge_density = np.sum(edges > 0) / (height * width)

    # ================ PHASE 0: PRIVACY PROTECTION CHECK ================
    # Check for humans in the image to protect people's privacy
    print("🛡️ Privacy Check: Scanning for humans in the image...")
    humans_detected = detect_humans_for_privacy(img_color)
    
    if humans_detected:
        print("🚫 Privacy Protection: Human detected - rejecting for privacy")
        return {
            'image_relevance_check': {
                'is_road_image': False,
                'reason': 'Privacy protection activated - analysis skipped',
                'ai_powered': False,
                'ai_confidence': 0.0,
                'note': 'Skipped due to privacy protection',
                'image_metrics': {
                    'dimensions': f"{width}x{height}",
                    'brightness': round(avg_brightness, 1),
                    'edge_density': round(edge_density, 4)
                }
            },
            'image_abuse_check': {
                'detected': False,
                'flags': [],
                'confidence': 0.0,
                'ai_powered': False,
                'note': 'Skipped due to privacy protection',
                'checks_performed': []
            },
            'text_abuse_check': {
                'detected': False,
                'flags': [],
                'description_length': len(description),
                'note': 'Skipped due to privacy protection',
                'checks_performed': []
            },
            'privacy_protection': {
                'humans_detected': True,
                'reason': 'Humans detected in image - privacy protection activated'
            },
            'final_decision': {
                'status': 'PRIVACY_PROTECTED',
                'accepted': False,
                'reason': 'Human detected in image. For privacy protection, please take a photo without people visible. This helps protect individual privacy in public reporting.',
                'strike_issued': False,
                'system_type': 'PRIVACY PROTECTION SYSTEM',
                'recommendation': 'Please retake the photo ensuring no people are visible in the frame.'
            },
            'user_message': {
                'description': description,
                'processed_at': 'Demo System'
            }
        }
    
    print("✅ Privacy Check: No humans detected - safe to proceed")
    
    # ================ PHASE 0.5: DOCUMENT/PAPER DETECTION (PRE-FILTER) ================
    # Critical check: Detect documents/papers BEFORE AI model to prevent false positives
    # Papers often look like roads to AI (textured, lines) but have specific characteristics
    
    is_document = False
    document_reason = ""
    
    # Method 1: Very bright surfaces (typical paper/document lighting)
    # OR surfaces with strong horizontal lines (notebook paper)
    
    # Check for text-like patterns (horizontal lines)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
    text_line_ratio = np.sum(horizontal_lines > 0) / (height * width)
    
    # Calculate histogram of grayscale image for uniformity check
    hist = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
    hist_norm = hist / (height * width)
    top_5_sum = np.sum(np.sort(hist_norm.flatten())[-5:])
    
    print(f"🔍 Document Debug: Brightness: {avg_brightness:.1f}, Line Ratio: {text_line_ratio:.4f}, Uniformity: {top_5_sum:.2f}")

    # Case A: Bright paper (Standard)
    if avg_brightness > 135:  
        if text_line_ratio > 0.002:
            is_document = True
            document_reason = "Text lines detected on bright surface (Document/Paper)"
            print(f"🚫 Document Pre-check: Text lines detected ({text_line_ratio:.4f})")
            
        if top_5_sum > 0.30: # Very uniform color distribution
            is_document = True
            document_reason = "Uniform bright surface detected (Document/Paper)"
            print(f"🚫 Document Pre-check: Uniform surface ({top_5_sum:.2f})")

    # Case B: Lined Notebook Paper (Robust Hough Line Check)
    # Lined paper has MANY parallel horizontal lines EVENLY DISTRIBUTED
    # Road markings are FEW lines (1-3) in specific zones
    # Use HoughLinesP to find long straight lines
    
    # Lower thresholds for Canny to catch faint lines
    edges_sensitive = cv2.Canny(img_gray, 30, 100)
    
    # Detect lines
    lines = cv2.HoughLinesP(edges_sensitive, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=10)
    
    if lines is not None:
        horizontal_line_count = 0
        line_positions = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            
            # Check for horizontal lines (0 degrees +/- 5)
            if angle < 5 or angle > 175:
                horizontal_line_count += 1
                line_positions.append(y1)  # Track vertical position
        
        print(f"🔍 Document Debug: Hough Horizontal Lines: {horizontal_line_count}")
        
        # CRITICAL: Distinguish notebook paper from road markings
        # Notebook paper: 15+ lines, evenly distributed across image height
        # Road markings: 1-5 lines, clustered in specific zones (center)
        
        if horizontal_line_count >= 15:  # Raised threshold from 5 to 15
            # Check if lines are evenly distributed (notebook pattern)
            if len(line_positions) > 0:
                line_positions.sort()
                # Calculate variance in spacing between consecutive lines
                spacings = [line_positions[i+1] - line_positions[i] for i in range(len(line_positions)-1)]
                if len(spacings) > 0:
                    avg_spacing = np.mean(spacings)
                    spacing_variance = np.var(spacings)
                    
                    # Notebook paper has consistent spacing (low variance)
                    # Road markings have irregular spacing (high variance)
                    if spacing_variance < (avg_spacing * 0.5):  # Consistent spacing
                        is_document = True
                        document_reason = f"Lined paper pattern detected ({horizontal_line_count} lines)"
                        print(f"🚫 Document Pre-check: Lined paper detected via Hough ({horizontal_line_count} lines)")
                    else:
                        print(f"✅ Road markings detected (irregular spacing, variance: {spacing_variance:.1f})")


    # Method 2: Aspect ratio check (papers are often rectangular)
    aspect_ratio = width / height if height > 0 else 1.0
    if (0.7 < aspect_ratio < 1.4) and avg_brightness > 130 and edge_density > 0.005:
         # Square-ish bright images with edges (text) are often documents
         # Double check for lack of road features (no dark asphalt)
         if np.percentile(img_gray, 10) > 80: # Even the darkest parts are bright
             is_document = True
             document_reason = "Bright rectangular object with text-like edges"
             print("🚫 Document Pre-check: Bright rectangular object detected")

    if is_document:
        print(f"🛑 BLOCKED: {document_reason}")
    
    # ================ PHASE 1: AI-POWERED ROAD RELEVANCE CHECK ================
    # Using YOUR TRAINED YOLO MODEL for accurate road detection!
    
    # Initialize all variables at the beginning to prevent scope issues
    is_road_image = False
    relevance_reason = ""
    ml_confidence = 0.0
    # is_document already initialized in Phase 0.5
    image_abuse_flags = []
    image_abuse_flags = []
    image_abuse_confidence = 0.0
    text_abuse_flags = []
    has_image_abuse = False
    has_text_abuse = False
    relevance_passed = False
    image_abuse_detected = False
    text_abuse_detected = False
    ai_road_decision_made = False  # Track if AI model made a decision
    
    # PRIMARY: Use enhanced road detection system (VSC + Colab models)
    if not is_document and enhanced_road_detector is not None:
        try:
            # Run enhanced road detection with lower threshold for better coverage
            road_results = enhanced_road_detector.detect_roads_enhanced(img_color, confidence_threshold=0.15)
            
            # FIX: Only use AI result if confidence is decent (>50%), otherwise use fallback
            # This handles cases where a weak model detects "something" with low confidence and blocks the fallback
            high_conf_detection = False
            if road_results["roads_detected"]:
                max_conf = max([d["confidence"] for d in road_results["detections"]])
                if max_conf > 0.50:
                    high_conf_detection = True
            
            if high_conf_detection:
                # Get the best detection from enhanced results
                best_detection = max(road_results["detections"], key=lambda x: x["confidence"])
                best_confidence = best_detection["confidence"]
                best_class = 0  # Road class
                
                # Use enhanced class names
                class_names = {0: 'road', 1: 'non-road'}
                predicted_class = class_names.get(best_class, f'class_{best_class}')
                
                ml_confidence = float(best_confidence)
                
                # STRICT Road detection logic with higher confidence requirements
                if 'road' in predicted_class.lower() or best_class == 0:  # Assuming class 0 is road
                    # Changed confidence threshold from 0.75 to 0.50
                    if best_confidence >= 0.50:
                        # ENHANCED VALIDATION: Additional checks for false positives
                        hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
                        
                        # Check for excessive green vegetation (bushes/nature)
                        # Green in HSV: Hue 35-85, Saturation 40-255, Value 40-255
                        green_mask = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
                        green_percentage = np.sum(green_mask > 0) / (height * width) * 100
                        
                        # Check for road-like linear features
                        edges = cv2.Canny(img_gray, 50, 150)
                        edge_density = np.sum(edges > 0) / (height * width)
                        
                        # Detect straight lines (roads have long straight edges)
                        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=width//4, maxLineGap=20)
                        has_linear_features = lines is not None and len(lines) > 5
                        
                        print(f"🔍 Validation: Green={green_percentage:.1f}%, Edges={edge_density:.4f}, Lines={has_linear_features}")
                        
                        # Calculate other metrics for validation
                        # Histogram analysis for diagrams/synthetic images
                        hist = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
                        hist_norm = hist / (height * width)
                        top_5_sum = np.sum(np.sort(hist_norm.flatten())[-5:])
                        
                        # Texture check (variance of Laplacian) - Real roads have texture, diagrams are flat
                        laplacian_var = cv2.Laplacian(img_gray, cv2.CV_64F).var()
                        
                        print(f"🔍 Debug: Synthetic Check - Top 5 Sum: {top_5_sum:.2f}, Laplacian Var: {laplacian_var:.1f}")
                        
                        # VALIDATION CHAIN: Check for various rejection criteria
                        # REJECT if it's mostly vegetation without road features
                        if green_percentage > 60 and not has_linear_features:
                            is_road_image = False
                            relevance_reason = f"AI Model: {predicted_class} detected ({best_confidence:.2f}) but image is pure vegetation - NOT a road"
                            print(f"🚫 Road detection overridden: Pure vegetation detected ({green_percentage:.1f}%)")
                        # REJECT if humans detected
                        elif humans_detected:
                            is_road_image = False
                            relevance_reason = f"AI Model: {predicted_class} detected ({best_confidence:.2f}) but image contains real humans - NOT road relevant"
                            print(f"🚫 Road detection overridden: Real human detected by privacy model")
                        # REJECT if too synthetic/uniform
                        elif top_5_sum > 0.35:
                            is_road_image = False
                            relevance_reason = f"AI Model: {predicted_class} detected ({best_confidence:.2f}) but image looks synthetic (uniform background) - NOT road relevant"
                            print(f"🚫 Road detection overridden: Synthetic/Uniform image detected (Top 5 colors: {top_5_sum*100:.1f}%)")
                        # REJECT if too flat (low texture)
                        elif laplacian_var < 50:
                            is_road_image = False
                            relevance_reason = f"AI Model: {predicted_class} detected ({best_confidence:.2f}) but image is too flat/synthetic - NOT road relevant"
                            print(f"🚫 Road detection overridden: Low texture variance ({laplacian_var:.1f})")
                        # ACCEPT - passed all validation checks
                        else:
                            is_road_image = True
                            relevance_reason = f"AI Model: {predicted_class} detected (confidence: {best_confidence:.2f}) - VALIDATED"
                            print(f"✅ Road detection validated: {best_confidence:.2f}")
                    else:
                        is_road_image = False
                        relevance_reason = f"AI Model: {predicted_class} confidence too low ({best_confidence:.2f} < 50%)"
                        print(f"⚪ Road detection rejected: Low confidence {best_confidence:.2f}")
                else:
                    is_road_image = False
                    relevance_reason = f"AI Model: {predicted_class} detected - not road relevant"
            else:
                # No objects detected OR confidence too low - use intelligent fallback
                print("🤔 No strong AI detections (>50%) - checking for road-like features...")
                
                # Smart fallback: Check for road characteristics
                gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
                
                # Check for linear features (road markings, edges)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / (height * width)
                
                # Reject high edge density (typical of text/screenshots)
                # RELAXED THRESHOLD: Increased from 0.15 to 0.35 to allow textured road images (gravel, trees, potholes)
                if edge_density > 0.35:
                    is_road_image = False
                    relevance_reason = f"Fallback: Image too complex/noisy (Edge Density: {edge_density:.2f}) - likely text or screenshot"
                    print(f"🚫 Fallback rejected: High edge density {edge_density:.2f}")
                else:
                    horizontal_lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=50)
                    
                    # Check for road-like texture
                    texture_variance = np.var(gray)
                    
                    # Check for road colors (asphalt grays, concrete whites)
                    avg_brightness = np.mean(gray)
                    
                    # SYNTHETIC CHECKS FOR FALLBACK
                    # Calculate histogram of grayscale image
                    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
                    hist_norm = hist / (height * width)
                    top_5_sum = np.sum(np.sort(hist_norm.flatten())[-5:])
                    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
                    
                    print(f"🔍 Debug: Fallback Synthetic Check - Top 5 Sum: {top_5_sum:.2f}, Laplacian Var: {laplacian_var:.1f}")
                    
                    # Road heuristic scoring
                    road_score = 0
                    
                    # PENALTY: Synthetic characteristics
                    if top_5_sum > 0.35:
                        road_score -= 500  # NUCLEAR PENALTY for uniform images
                        print("🚫 Fallback Penalty: Synthetic/Uniform image detected")
                    if laplacian_var < 50:
                        road_score -= 500  # NUCLEAR PENALTY for flat images
                        print("🚫 Fallback Penalty: Low texture variance")
                    
                    if horizontal_lines is not None and len(horizontal_lines) > 2:
                        road_score += 30  # Linear features found
                    if 40 < avg_brightness < 180:
                        road_score += 25  # Road-like brightness
                    if 500 < texture_variance < 3000:
                        road_score += 20  # Road-like texture
                    
                    # Check for road surface patterns
                    height, width = gray.shape
                    bottom_third = gray[2*height//3:, :]
                    bottom_variance = np.var(bottom_third)
                    if bottom_variance > 200:  # Textured surface in bottom third
                        road_score += 25
                    
                    print(f"📊 Fallback road score: {road_score}/100")
                    
                    if road_score >= 50:  # Threshold for road-like image
                        is_road_image = True
                        relevance_reason = f"Smart Fallback: Road-like features detected (score: {road_score}/100)"
                        print(f"✅ Fallback detection: Likely road image")
                    else:
                        # EMERGENCY DETECTOR: Last resort for difficult cases
                        # CRITICAL FIX: Do NOT use emergency detector if image was penalized as synthetic
                        if road_score < 0:  # Any negative score means it was penalized
                            is_road_image = False
                            relevance_reason = f"Synthetic/Document detected (Score: {road_score}/100) - Emergency detection skipped"
                            print(f"🚫 Emergency detection skipped due to synthetic penalty")
                        else:
                            print("🚨 Activating Emergency Road Detector...")
                            emergency_detector = EmergencyRoadDetector()
                            emergency_result = emergency_detector.detect_road_emergency(img_color)
                            
                            if emergency_result["is_road"]:
                                is_road_image = True
                                relevance_reason = f"Emergency Detection: {emergency_result['method']} (confidence: {emergency_result['confidence']:.1f}%)"
                                print(f"✅ Emergency detection successful: {', '.join(emergency_result['indicators'])}")
                            else:
                                is_road_image = False
                                relevance_reason = "All Detection Methods: No road features detected in image"
                
            print(f"🤖 AI Road Detection: {relevance_reason}")
            ai_road_decision_made = True  # AI model has made a decision
            
        except Exception as e:
            print(f"⚠️ Enhanced road detection error: {e}")
            # Fall back to heuristics if AI fails
            enhanced_road_detector = None
    
    # FALLBACK: Enhanced heuristics ONLY if AI model unavailable OR failed to make decision
    # AND if not already identified as a document
    if not is_document and (enhanced_road_detector is None or not ai_road_decision_made):
        if not ai_road_decision_made:
            print("🔄 Using fallback heuristic detection")
        else:
            print("🔄 AI model unavailable, using heuristic detection")
        # Note: avg_brightness, edges, edge_density already calculated above
        # Note: is_document already initialized above
        
        # ENHANCED Document/Paper Detection - More comprehensive!
        
        # Multiple ways to detect documents/papers
        
        # Method 1: Very bright surfaces (typical paper/document lighting)
        if avg_brightness > 140:  # Lowered threshold for better detection
            is_document = True
            relevance_reason = "Very bright surface - likely paper/document"
    
        # Method 2: SPECIFIC text detection (avoid road damage patterns)
        if avg_brightness > 120 and edge_density > 0.003:  # Only for bright images with edges
            # Text patterns are different from road damage - they're more regular
            # Check for horizontal line patterns (text lines)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
            text_line_ratio = np.sum(horizontal_lines > 0) / (height * width)
            
            # Text has regular horizontal lines, roads have irregular damage
            if text_line_ratio > 0.002 and avg_brightness > 130:  # Bright + horizontal lines = text
                is_document = True
                relevance_reason = "Text line patterns detected - document/paper image"
    
        # Method 3: Aspect ratio check (papers are often rectangular)
        aspect_ratio = width / height if height > 0 else 1.0
        if (aspect_ratio > 0.7 and aspect_ratio < 1.4) and avg_brightness > 120:
            # Square-ish bright images are often documents
            is_document = True
            relevance_reason = "Rectangular bright surface - likely document"
    
        # Method 4: SPECIFIC paper detection (avoid bright roads)
        if avg_brightness > 160:  # Higher threshold - only very bright surfaces
            # Check if image is mostly grayscale AND lacks road features
            b, g, r = cv2.split(img_color)
            color_variance = np.var([np.mean(b), np.mean(g), np.mean(r)])
            
            # Look for road-specific features to EXCLUDE from document detection
            # Check for lane markings or road patterns
            hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
            white_mask = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 30, 255]))
            white_ratio = np.sum(white_mask > 0) / (height * width)
            
            # If it has white markings (lane lines), it's likely a road, not a document
            if color_variance < 80 and white_ratio < 0.05:  # Very grayscale + no road markings
                is_document = True
                relevance_reason = "Pure white/gray surface - document detected"
    
        # Final heuristic road classification
        # If it's a document, immediately reject - NO EXCEPTIONS!
        if is_document:
            is_road_image = False
        # Too dark to be useful road image  
        elif avg_brightness < 40:
            is_road_image = False
            relevance_reason = "Too dark - road features not visible"
        else:
            # EXPANDED road detection - accept well-lit roads too
            if 40 <= avg_brightness <= 160:  # WIDER brightness range (includes well-lit roads)
                # Roads need some texture but be flexible
                if edge_density >= 0.01:  # Lower threshold - accept cleaner roads
                    # Check for road-specific indicators
                    hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
                    saturation_mean = np.mean(hsv[:,:,1])
                    
                    # Look for road markings (white lines) - strong road indicator
                    white_mask = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 30, 255]))
                    white_ratio = np.sum(white_mask > 0) / (height * width)
                    
                    # If has lane markings, definitely a road
                    if white_ratio > 0.02:  # Has white lane markings
                        is_road_image = True
                        relevance_reason = "Road with lane markings detected"
                    # Otherwise check saturation (roads are typically unsaturated)
                    elif saturation_mean < 100:  # Unsaturated (asphalt-like or well-lit road)
                        # Check for any road-like features
                        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        features = sum(1 for c in contours if cv2.contourArea(c) > 30)
                        
                        if features >= 2:  # Minimal features required
                            is_road_image = True
                            relevance_reason = "Road surface detected"
                        else:
                            is_road_image = False
                            relevance_reason = "Lacks road features - too uniform"
                    else:
                        is_road_image = False
                        relevance_reason = "Too colorful - not road-like"
                else:
                    is_road_image = False
                    relevance_reason = "Too uniform - no road texture visible"
            else:
                is_road_image = False
                relevance_reason = "Brightness outside road range (too bright for asphalt)"
    
    # End of heuristic logic - AI decision takes precedence
    
    # ================ PHASE 2: AI-POWERED ABUSE DETECTION ================
    # Using YOUR TRAINED YOLO MODEL for accurate abuse/weapon detection!
    # Note: image_abuse_flags and image_abuse_confidence already initialized above
    
    # PRIMARY: Use your trained YOLO abuse detection model
    if abuse_model is not None:
        try:
            # Run abuse detection inference
            abuse_results = abuse_model(img_color, verbose=False)
            
            if len(abuse_results) > 0 and len(abuse_results[0].boxes) > 0:
                # Process all detections
                confidences = abuse_results[0].boxes.conf.cpu().numpy()
                classes = abuse_results[0].boxes.cls.cpu().numpy()
                
                # Get class names
                class_names = abuse_results[0].names if hasattr(abuse_results[0], 'names') else {0: 'weapon', 1: 'violence', 2: 'inappropriate'}
                
                detected_abuse = []
                max_confidence = 0.0
                
                # ENHANCED FILTERING: Higher thresholds and better class analysis
                for i, (conf, cls) in enumerate(zip(confidences, classes)):
                    class_name = class_names.get(int(cls), f'abuse_class_{int(cls)}').lower()
                    
                    # STRICTER CONFIDENCE THRESHOLDS based on class
                    confidence_threshold = 0.70  # Default: High threshold (70%)
                    
                    # Adjust thresholds based on class type
                    if 'weapon' in class_name or 'gun' in class_name or 'knife' in class_name:
                        confidence_threshold = 0.50  # Lower for weapons (50%) - weapons are critical!
                    elif 'violence' in class_name or 'blood' in class_name:
                        confidence_threshold = 0.70  # Medium for violence (70%)
                    elif 'abusive' in class_name and len(class_name) <= 8:  # Generic "abusive" class
                        confidence_threshold = 0.85  # Very high for generic class (85%)
                    
                    # Only flag if confidence is above the strict threshold
                    if conf > confidence_threshold:
                        detected_abuse.append(f"{class_name} ({conf:.2f})")
                        max_confidence = max(max_confidence, conf)
                        print(f"🔍 High confidence detection: {class_name} at {conf:.2f} (threshold: {confidence_threshold})")
                    else:
                        print(f"⚪ Low confidence ignored: {class_name} at {conf:.2f} (threshold: {confidence_threshold})")
                
                # ADDITIONAL VALIDATION: Check for false positives
                if detected_abuse:
                    # Filter out likely false positives for normal human images
                    valid_detections = []
                    
                    for detection in detected_abuse:
                        detection_lower = detection.lower()
                        
                        # Extract confidence from detection string (format: "name (0.XX)")
                        try:
                            conf_str = detection.split('(')[1].split(')')[0]
                            detection_conf = float(conf_str)
                        except:
                            detection_conf = 0.0
                        
                        # CRITICAL FIX: Don't filter out HIGH confidence detections (>= 80%)
                        # If the model is very confident, trust it even if class name is generic
                        if detection_conf >= 0.80:
                            print(f"✅ High confidence detection kept: {detection}")
                            valid_detections.append(detection)
                            continue
                        
                        # Only filter LOW confidence generic "abusive" detections
                        if ('abusive' in detection_lower and 
                            'weapon' not in detection_lower and 
                            'gun' not in detection_lower and
                            'knife' not in detection_lower and
                            'violence' not in detection_lower and
                            detection_conf < 0.80):
                            # This might be a normal human image misclassified
                            print(f"🤔 Low confidence generic detection filtered: {detection}")
                            continue
                        
                        valid_detections.append(detection)
                    
                    if valid_detections:
                        image_abuse_flags.extend([f"AI Abuse Detection: {item}" for item in valid_detections])
                        image_abuse_confidence = float(max_confidence)
                        print(f"🚨 CONFIRMED ABUSE DETECTED: {', '.join(valid_detections)}")
                    else:
                        print("✅ All detections filtered as false positives - likely normal human image")
                else:
                    print("✅ AI Model: No high-confidence abusive content detected")
            else:
                print("✅ AI Model: No abusive objects detected")
                
        except Exception as e:
            print(f"⚠️ AI abuse model error: {e}")
            abuse_model = None
    
    # FALLBACK: Enhanced heuristic detection if AI model unavailable
    if abuse_model is None:
        print("🔄 Using fallback abuse detection heuristics")
        
        # Basic weapon detection
        edges_strong = cv2.Canny(img_gray, 100, 200)
        contours, _ = cv2.findContours(edges_strong, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        weapon_indicators = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 800 < area < 25000:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                if aspect_ratio >= 2.0 or aspect_ratio <= 0.8:
                    weapon_indicators += 1
        
        if weapon_indicators >= 2:
            image_abuse_flags.append("Heuristic weapon detection")
            image_abuse_confidence += 0.6
    
    # 2. VIOLENCE/BLOOD DETECTION  
    # Check for red color dominance indicating blood (avoid road markings)
    red_channel = img_color[:,:,2]  # BGR format, red is index 2
    red_mean = np.mean(red_channel)
    red_std = np.std(red_channel)
    
    # More specific blood detection (avoid red road signs, brake lights)
    if red_mean > 150 and red_std > 60:  # Very high red content with high variation
        # Additional check: look for organic blood-like patterns
        hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
        red_hue_mask = cv2.inRange(hsv, np.array([0, 50, 50]), np.array([10, 255, 255]))
        red_percentage = np.sum(red_hue_mask > 0) / (height * width) * 100
        
        if red_percentage > 8:  # Significant red area
            image_abuse_flags.append("Potential blood/violence content")
            image_abuse_confidence += 0.4
    
    # 3. INAPPROPRIATE CONTENT DETECTION
    # Check for skin-colored regions (avoid road lighting false positives)
    hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
    # More specific skin color range to avoid road surface false positives
    skin_mask = cv2.inRange(hsv, np.array([0, 40, 80]), np.array([25, 255, 255]))
    skin_percentage = np.sum(skin_mask > 0) / (height * width) * 100
    
    # Much higher threshold to avoid road surface false positives
    if skin_percentage > 35:  # Very high skin content
        # Additional validation: check for human-like shapes
        contours_skin, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_skin_regions = [c for c in contours_skin if cv2.contourArea(c) > 2000]
        
        if len(large_skin_regions) >= 2:  # Multiple large skin-colored regions
            image_abuse_flags.append("Potential inappropriate content")
            image_abuse_confidence += 0.5
    
    # ENHANCED FINAL VALIDATION: Additional checks to prevent false positives
    # Check if this might be a normal human image being misclassified
    if len(image_abuse_flags) > 0:
        # Analyze image characteristics to validate abuse detection
        hsv = cv2.cvtColor(img_color, cv2.COLOR_BGR2HSV)
        
        # Check for skin tone presence (normal humans have skin)
        skin_mask = cv2.inRange(hsv, np.array([0, 40, 80]), np.array([25, 255, 255]))
        skin_percentage = np.sum(skin_mask > 0) / (height * width) * 100
        
        # Check for normal photo characteristics
        is_normal_photo = False
        if (20 < skin_percentage < 40 and  # Reasonable amount of skin (normal human)
            80 < avg_brightness < 200 and  # Normal lighting
            image_abuse_confidence < 0.98):  # Not extremely high confidence
            is_normal_photo = True
            print(f"🤔 Image has normal human characteristics: skin={skin_percentage:.1f}%, brightness={avg_brightness:.1f}")
        
        # If it looks like a normal photo, require VERY high confidence for abuse flagging
        # BUT NEVER FILTER WEAPONS/GUNS
        
        has_weapon_flag = any("weapon" in flag.lower() or "gun" in flag.lower() for flag in image_abuse_flags)
        
        if is_normal_photo and not has_weapon_flag:
            if image_abuse_confidence < 0.95:  # Require 95%+ confidence for normal-looking photos
                print("✅ OVERRIDE: Filtering abuse detection - appears to be normal human image")
                image_abuse_flags = []  # Clear the flags
                image_abuse_confidence = 0.0
            else:
                print(f"🚨 HIGH CONFIDENCE ABUSE CONFIRMED: {image_abuse_confidence:.2f} - overriding normal photo filter")
        elif has_weapon_flag:
             print(f"🚨 WEAPON DETECTED: {image_abuse_confidence:.2f} - bypassing normal photo filter")
    
    # Final image abuse assessment
    has_image_abuse = len(image_abuse_flags) > 0 or image_abuse_confidence > 0.4
    
    # ================ PHASE 3: GOVERNMENT-LEVEL TEXT FILTERING ================
    # EXTREMELY STRICT for Sri Lankan government issue reporting platform
    # Note: text_abuse_flags already initialized above
    
    text_lower = description.lower()
    
    # 1. PROFANITY & INAPPROPRIATE LANGUAGE (COMPREHENSIVE)
    profanity_words = [
        # Basic profanity
        'fuck', 'shit', 'damn', 'hell', 'bastard', 'bitch', 'ass', 'crap', 
        'piss', 'bloody', 'asshole', 'dickhead', 'motherfucker', 'whore',
        'slut', 'cock', 'dick', 'pussy', 'tits', 'boobs', 'penis', 'vagina',
        
        # Insults & derogatory terms
        'idiot', 'stupid', 'moron', 'fool', 'dumbass', 'jackass', 'retard',
        'loser', 'pathetic', 'worthless', 'useless', 'garbage', 'trash',
        'pity', 'pitiful', 'shameful', 'disgusting', 'horrible', 'awful',
        'terrible', 'worst', 'suck', 'sucks', 'bullshit', 'nonsense',
        
        # Mental health slurs
        'crazy', 'insane', 'mad', 'psycho', 'mental', 'lunatic', 'nuts',
        'retarded', 'disabled', 'handicapped',
        
        # Body shaming
        'fat', 'ugly', 'hideous', 'gross', 'disgusting', 'repulsive',
        
        # Dismissive language
        'whatever', 'shut up', 'get lost', 'go away', 'buzz off',
        'mind your business', 'none of your business'
    ]
    profanity_found = [word for word in profanity_words if word in text_lower]
    if profanity_found:
        text_abuse_flags.append(f"Inappropriate language: {', '.join(profanity_found)}")
    
    # 2. ETHNIC/COMMUNITY TARGETING (Sri Lankan context)
    ethnic_targeting = [
        'tamil', 'sinhala', 'sinhalese', 'muslim', 'christian', 'buddhist', 
        'hindu', 'burgher', 'malay', 'veddah', 'tamil tigers', 'jvp',
        'ethnic', 'race', 'community', 'minority', 'majority'
    ]
    ethnic_found = [word for word in ethnic_targeting if word in text_lower]
    if ethnic_found:
        text_abuse_flags.append(f"Community targeting: {', '.join(ethnic_found)}")
    
    # 3. POLITICAL TARGETING & GOVERNMENT CRITICISM  
    political_words = [
        'president', 'minister', 'mp', 'politician', 'government', 'parliament',
        'mahinda', 'gotabaya', 'ranil', 'sajith', 'anura', 'maithripala',
        'corruption', 'corrupt', 'bribe', 'political', 'party', 'election'
    ]
    political_found = [word for word in political_words if word in text_lower]
    if political_found:
        text_abuse_flags.append(f"Political content: {', '.join(political_found)}")
    
    # 4. WEAPONS & DANGEROUS ITEMS (COMPREHENSIVE)
    weapon_words = [
        # Firearms
        'gun', 'guns', 'pistol', 'rifle', 'shotgun', 'revolver', 'firearm',
        'ak47', 'ak-47', 'ar15', 'ar-15', 'glock', 'beretta', 'colt',
        'weapon', 'weapons', 'bullet', 'bullets', 'ammunition', 'ammo',
        'trigger', 'barrel', 'magazine', 'clip', 'scope', 'silencer',
        
        # Explosives
        'bomb', 'bombs', 'explosive', 'explosives', 'grenade', 'dynamite',
        'c4', 'tnt', 'blast', 'detonate', 'explosion', 'landmine',
        
        # Bladed weapons
        'knife', 'knives', 'blade', 'sword', 'dagger', 'machete',
        'razor', 'cutting', 'stab', 'stabbing', 'slice', 'slicing'
    ]
    weapon_found = [word for word in weapon_words if word in text_lower]
    if weapon_found:
        text_abuse_flags.append(f"Weapon references: {', '.join(weapon_found)}")
    
    # 5. TERROR GROUPS & EXTREMISM
    terror_words = [
        'ltte', 'tiger', 'prabhakaran', 'terrorist', 'terrorism', 'bomb', 
        'attack', 'war', 'violence', 'militant', 'extremist', 'separatist',
        'tamil eelam', 'suicide', 'killing', 'murder'
    ]
    terror_found = [word for word in terror_words if word in text_lower]
    if terror_found:
        text_abuse_flags.append(f"Extremist content: {', '.join(terror_found)}")
    
    # 6. THREATS & VIOLENCE
    threat_patterns = [
        'kill', 'die', 'death', 'murder', 'destroy', 'attack', 'bomb',
        'i will', 'going to', 'watch out', 'you better', 'threat', 'hurt',
        'harm', 'revenge', 'punish', 'beat', 'shoot', 'shooting', 'fire',
        'burn', 'torture', 'abuse', 'violence', 'violent', 'dangerous'
    ]
    threat_found = [word for word in threat_patterns if word in text_lower]
    if threat_found:
        text_abuse_flags.append(f"Threatening language: {', '.join(threat_found)}")
    
    # 6. HATE SPEECH & DISCRIMINATION
    hate_speech = [
        'hate', 'discrimination', 'racist', 'racism', 'prejudice', 'bigot',
        'supremacy', 'inferior', 'superior', 'enemy', 'traitor', 'betrayal'
    ]
    hate_found = [word for word in hate_speech if word in text_lower]
    if hate_found:
        text_abuse_flags.append(f"Hate speech: {', '.join(hate_found)}")
    
    # 7. INFLAMMATORY LANGUAGE
    inflammatory = [
        'uprising', 'revolt', 'revolution', 'overthrow', 'rebellion',
        'protest', 'riot', 'chaos', 'anarchy', 'conflict', 'fight'
    ]
    inflammatory_found = [word for word in inflammatory if word in text_lower]
    if inflammatory_found:
        text_abuse_flags.append(f"Inflammatory content: {', '.join(inflammatory_found)}")
    
    # 8. ADDITIONAL INAPPROPRIATE PATTERNS
    inappropriate_patterns = [
        # Questioning/dismissive phrases  
        'what a', 'such a', 'so stupid', 'how stupid', 'why so',
        'what nonsense', 'total nonsense', 'complete nonsense',
        
        # Condescending language
        'obviously', 'clearly you', 'you should know', 'common sense',
        'use your brain', 'think before', 
        
        # Dismissive expressions
        'i dont care', 'who cares', 'nobody cares', 'not my problem',
        'deal with it', 'too bad', 'so what', 'big deal'
    ]
    
    for pattern in inappropriate_patterns:
        if pattern in text_lower:
            text_abuse_flags.append(f"Inappropriate expression: {pattern}")
    
    # 9. NEGATIVE EMOTIONAL LANGUAGE (for sensitive government platform)
    negative_emotions = [
        'hate', 'angry', 'furious', 'pissed off', 'annoyed', 'irritated',
        'fed up', 'sick of', 'tired of', 'disgusted', 'frustrated',
        'outraged', 'livid', 'mad', 'upset'
    ]
    negative_found = [word for word in negative_emotions if word in text_lower]
    if negative_found:
        text_abuse_flags.append(f"Negative emotional language: {', '.join(negative_found)}")
    
    # 10. AI-POWERED TEXT ANALYSIS (Hybrid Approach)
    # This runs ALONGSIDE the rule-based checks to catch context-dependent abuse (sarcasm, etc.)
    ai_text_confidence = 0.0
    ai_text_label = "SAFE"
    
    if DISTILBERT_AVAILABLE and distilbert_pipeline is not None:
        try:
            is_abusive_ai, label_ai, confidence_ai = analyze_text_with_ai(description)
            ai_text_confidence = confidence_ai
            ai_text_label = label_ai
            
            if is_abusive_ai:
                text_abuse_flags.append(f"AI Context Analysis: {label_ai} ({confidence_ai:.1%})")
                print(f"🤖 AI Text Alert: {label_ai} ({confidence_ai:.2f})")
            else:
                print(f"✅ AI Text Check: Safe ({confidence_ai:.2f})")
        except Exception as e:
            print(f"⚠️ AI Text Analysis Failed: {e}")
    
    # FINAL TEXT ASSESSMENT - ANY flag means rejection for government platform
    has_text_abuse = len(text_abuse_flags) > 0
    
    # ================ FINAL DECISION LOGIC ================
    
    # THREE SEPARATE CHECKS:
    
    # 1. IMAGE RELEVANCE: Is it a road image? (based on your road dataset)
    relevance_passed = is_road_image
    
    # 2. IMAGE ABUSE: Does it contain weapons/inappropriate content?
    image_abuse_detected = has_image_abuse
    
    # 3. TEXT ABUSE: Does the text contain inappropriate language?
    text_abuse_detected = has_text_abuse
    
    # ================ PHASE 4: GARBAGE CLASSIFICATION (FOR ALL IMAGES) ================
    # This classifies ANY image as containing garbage or being clean
    # Useful even for non-road images to detect garbage in the scene
    
    garbage_status = "unknown"
    garbage_confidence = 0.0
    
    if garbage_model is not None:
        try:
            print("🗑️ Running garbage classification...")
            results = garbage_model.predict(img_color, verbose=False)
            
            if results and len(results) > 0:
                probs = results[0].probs
                predicted_class = probs.top1  # 0 = clean, 1 = garbage
                confidence = probs.top1conf.item()
                
                if predicted_class == 0:
                    garbage_status = "clean"
                    garbage_confidence = confidence
                    print(f"✅ Image is CLEAN (confidence: {confidence:.2%})")
                else:
                    garbage_status = "garbage_detected"
                    garbage_confidence = confidence
                    print(f"🗑️ Image has GARBAGE (confidence: {confidence:.2%})")
        except Exception as e:
            print(f"⚠️ Garbage classification failed: {e}")
            garbage_status = "error"
    
    # FINAL DECISION LOGIC
    if is_document:
        final_status = "REJECTED - NOT A ROAD IMAGE"
        final_reason = f"Image relevance check failed: Not road-related content"
        strike_issued = False
        relevance_passed = False # Ensure it fails relevance check
    elif not relevance_passed:
        final_status = "REJECTED - NOT A ROAD IMAGE"
        final_reason = f"Image relevance check failed: {relevance_reason}"
        strike_issued = False
    elif image_abuse_detected:
        final_status = "REJECTED - ABUSIVE IMAGE CONTENT"
        final_reason = f"Image contains: {', '.join(image_abuse_flags)}"
        strike_issued = True  # Strike for abusive image
    elif text_abuse_detected:
        final_status = "REJECTED - ABUSIVE TEXT CONTENT"
        final_reason = f"Text contains: {', '.join(text_abuse_flags)}"
        strike_issued = True  # Strike for abusive text
    else:
        final_status = "ACCEPTED"
        final_reason = "Road image + Clean content"
        strike_issued = False
    
    # AI-ENHANCED RESULT STRUCTURE
    result = {
        'image_relevance_check': {
            'is_road_image': relevance_passed if not humans_detected else None,  # None if privacy failed
            'reason': relevance_reason if not humans_detected else 'Skipped due to privacy protection',
            'ai_powered': enhanced_road_detector is not None,
            'ai_confidence': round(ml_confidence, 3) if ml_confidence > 0 and not humans_detected else None,
            'note': 'Skipped due to privacy protection' if humans_detected else ('Enhanced AI road detection using BOTH VSC + Colab trained models' if enhanced_road_detector else 'Fallback heuristic detection'),
            'image_metrics': {
                'dimensions': f"{width}x{height}",
                'brightness': round(avg_brightness, 1),
                'edge_density': round(edge_density, 4)
            }
        },
        'image_abuse_check': {
            'detected': image_abuse_detected,
            'flags': image_abuse_flags,
            'confidence': round(image_abuse_confidence, 2),
            'ai_powered': abuse_model is not None,
            'note': 'AI-powered abuse detection using YOUR trained YOLO model' if abuse_model else 'Fallback heuristic detection',
            'checks_performed': [
                'AI Weapon/gun detection (trained on your dataset)' if abuse_model else 'Heuristic weapon detection',
                'Blood/violence detection',
                'Inappropriate content detection'
            ]
        },
        'text_abuse_check': {
            'detected': text_abuse_detected,
            'flags': text_abuse_flags,
            'description_length': len(description),
            'note': 'Only checks text language - separate from image analysis',
            'checks_performed': [
                'Profanity detection',
                'Hate speech detection', 
                'Threat detection',
                'AI Context Analysis (DistilBERT)' if distilbert_pipeline else 'Keyword filtering only'
            ],
            'ai_powered': distilbert_pipeline is not None,
            'ai_confidence': round(ai_text_confidence, 2) if distilbert_pipeline else 0.0,
            'ai_label': ai_text_label if distilbert_pipeline else None
        },
        'final_decision': {
            'status': final_status,
            'accepted': final_status == "ACCEPTED",
            'reason': final_reason,
            'strike_issued': strike_issued,
            'system_type': 'AI-ENHANCED HARISH FILTERATION SYSTEM',
            'models_loaded': {
                'road_detection': enhanced_road_detector is not None,
                'abuse_detection': abuse_model is not None
            }
        },
        'user_message': {
            'description': description,
            'processed_at': 'Demo System'
        },
        'privacy_protection': {
            'humans_detected': False,
            'reason': 'No humans detected - privacy check passed'
        },
        'garbage_classification': {
            'status': garbage_status,
            'confidence': round(garbage_confidence, 2) if garbage_confidence > 0 else 0.0,
            'ai_powered': garbage_model is not None,
            'note': 'Classification model trained at 100% accuracy' if garbage_model else 'Model not loaded',
            'message': {
                'clean': '✅ Road is clean and well-maintained',
                'garbage_detected': '🗑️ Road has visible garbage or waste',
                'unknown': '❓ Garbage status not checked (not a road image)',
                'error': '⚠️ Classification failed'
            }.get(garbage_status, '')
        }
    }
    
    return result

# ==========================================
# FLASK ROUTES
# ==========================================

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Road Issue Reporting - AI Demo</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }
        .container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .upload-section { border: 2px dashed #3498db; padding: 40px; text-align: center; border-radius: 10px; margin-bottom: 20px; transition: all 0.3s ease; }
        .upload-section:hover { background-color: #ecf0f1; border-color: #2980b9; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #34495e; }
        textarea { width: 100%; padding: 10px; border: 1px solid #bdc3c7; border-radius: 5px; min-height: 100px; font-family: inherit; }
        button { background-color: #2ecc71; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 5px; cursor: pointer; width: 100%; transition: background-color 0.3s; }
        button:hover { background-color: #27ae60; }
        #result { margin-top: 30px; display: none; }
        .result-card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 15px; }
        .status-accepted { background-color: #d4edda; border-color: #c3e6cb; color: #155724; }
        .status-rejected { background-color: #f8d7da; border-color: #f5c6cb; color: #721c24; }
        .metric { display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        .metric:last-child { border-bottom: none; }
        .loader { border: 5px solid #f3f3f3; border-top: 5px solid #3498db; border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 20px auto; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .preview-image { max-width: 100%; max-height: 300px; margin-top: 15px; border-radius: 5px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛣️ Road Issue Reporting AI</h1>
        
        <div class="upload-section">
            <input type="file" id="imageInput" accept="image/*" style="display: none;">
            <button onclick="document.getElementById('imageInput').click()" style="background-color: #3498db; width: auto; margin-bottom: 10px;">📸 Select Road Image</button>
            <p id="fileName">No file selected</p>
            <img id="imagePreview" class="preview-image">
        </div>

        <div class="form-group">
            <label for="description">Issue Description:</label>
            <textarea id="description" placeholder="Describe the road issue (e.g., 'Large pothole causing traffic jam')..."></textarea>
        </div>

        <button onclick="analyzeContent()">🔍 Analyze Content</button>
        <div id="loader" class="loader"></div>

        <div id="result"></div>
    </div>

    <script>
        const imageInput = document.getElementById('imageInput');
        const imagePreview = document.getElementById('imagePreview');
        const fileName = document.getElementById('fileName');
        let base64Image = "";

        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                fileName.textContent = file.name;
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                    base64Image = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });

        async function analyzeContent() {
            if (!base64Image) {
                alert("Please select an image first!");
                return;
            }

            const description = document.getElementById('description').value;
            const loader = document.getElementById('loader');
            const resultDiv = document.getElementById('result');
            
            loader.style.display = 'block';
            resultDiv.style.display = 'none';

            try {
                const response = await fetch('/api/check_image', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: base64Image,
                        description: description
                    })
                });

                const data = await response.json();
                displayResult(data);
            } catch (error) {
                alert("Error analyzing content: " + error.message);
            } finally {
                loader.style.display = 'none';
                resultDiv.style.display = 'block';
            }
        }

        function displayResult(data) {
            const resultDiv = document.getElementById('result');
            
            // ERROR HANDLING: Check if backend returned an error
            if (data.error) {
                resultDiv.innerHTML = `
                    <div class="result-card status-rejected">
                        <h2>❌ Error Analyzing Image</h2>
                        <p style="font-size: 1.1em; margin: 10px 0;"><strong>Reason:</strong> ${data.error}</p>
                        <p style="color: #666;">Please try a different image format (JPG, PNG).</p>
                    </div>
                `;
                return;
            }

            const decision = data.final_decision;
            const statusClass = decision.accepted ? 'status-accepted' : 'status-rejected';
            const icon = decision.accepted ? '✅' : '❌';

            let html = `
                <div class="result-card ${statusClass}">
                    <h2>${icon} Final Decision: ${decision.status}</h2>
                    <p style="font-size: 1.1em; margin: 10px 0;"><strong>Reason:</strong> ${decision.reason}</p>
                    ${decision.recommendation ? `<p style="color: #d35400; background: #fdebd0; padding: 10px; border-radius: 5px;"><strong>💡 Recommendation:</strong> ${decision.recommendation}</p>` : ''}
                    <p style="font-size: 0.8em; color: #666; margin-top: 10px;">System: ${decision.system_type}</p>
                </div>

                <div class="result-card">
                    <h3>🛣️ Road Relevancy Check</h3>
                    <div class="metric">
                        <span>Is Road Image?</span>
                        <span>${data.image_relevance_check.is_road_image === null ? '⏭️ N/A' : (data.image_relevance_check.is_road_image ? '✅ Yes' : '❌ No')}</span>
                    </div>
                    <div class="metric">
                        <span>Confidence</span>
                        <span>${data.image_relevance_check.ai_confidence ? (data.image_relevance_check.ai_confidence * 100).toFixed(1) + '%' : 'N/A'}</span>
                    </div>
                    <div class="metric">
                        <span>Method</span>
                        <span>${data.image_relevance_check.note}</span>
                    </div>
                    
                    <h4 style="margin-top: 15px; border-bottom: 1px solid #eee; padding-bottom: 5px;">📊 Image Metrics</h4>
                    <div class="metric">
                        <span>Dimensions</span>
                        <span>${data.image_relevance_check.image_metrics ? data.image_relevance_check.image_metrics.dimensions : 'N/A'}</span>
                    </div>
                    <div class="metric">
                        <span>Brightness</span>
                        <span>${data.image_relevance_check.image_metrics ? data.image_relevance_check.image_metrics.brightness : 'N/A'}</span>
                    </div>
                    <div class="metric">
                        <span>Edge Density</span>
                        <span>${data.image_relevance_check.image_metrics ? data.image_relevance_check.image_metrics.edge_density : 'N/A'}</span>
                    </div>
                    
                    ${data.garbage_classification && data.garbage_classification.status !== 'unknown' ? `
                    <h4 style="margin-top: 15px; border-bottom: 1px solid #eee; padding-bottom: 5px;">🗑️ Road Cleanliness</h4>
                    <div class="metric">
                        <span>Status</span>
                        <span style="font-weight: bold; color: ${data.garbage_classification.status === 'clean' ? '#27ae60' : '#e74c3c'};">
                            ${data.garbage_classification.status === 'clean' ? '✅ CLEAN' : '🗑️ GARBAGE DETECTED'}
                        </span>
                    </div>
                    <div class="metric">
                        <span>Confidence</span>
                        <span>${(data.garbage_classification.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <p style="font-size: 0.85em; color: #666; margin-top: 8px; font-style: italic;">
                        ${data.garbage_classification.message}
                    </p>
                    ` : ''}
                </div>

                <div class="result-card">
                    <h3>🛡️ Abuse & Safety Check</h3>
                    <div class="metric">
                        <span>Human Detection</span>
                        <span>${data.privacy_protection && !data.privacy_protection.humans_detected ? '✅ Passed' : '❌ Failed'}</span>
                    </div>
                    <div class="metric">
                        <span>Abusive Content?</span>
                        <span>${data.image_abuse_check.detected ? '❌ Detected' : '✅ Clean'}</span>
                    </div>
                    <div class="metric">
                        <span>Flags</span>
                        <span>${data.image_abuse_check.flags.length > 0 ? data.image_abuse_check.flags.join(', ') : 'None'}</span>
                    </div>
                     <div class="metric">
                        <span>Confidence</span>
                        <span>${data.image_abuse_check.confidence ? (data.image_abuse_check.confidence * 100).toFixed(1) + '%' : '0%'}</span>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.9em; color: #555;">
                        <strong>Checks Performed:</strong>
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            ${data.image_abuse_check.checks_performed ? data.image_abuse_check.checks_performed.map(check => `<li>${check}</li>`).join('') : '<li>Standard checks</li>'}
                        </ul>
                    </div>
                </div>

            <div class="result-card">
                <h3>📝 Text Analysis</h3>
                <div class="metric">
                    <span>Abusive Text?</span>
                    <span>${data.text_abuse_check.detected ? '❌ Detected' : '✅ Clean'}</span>
                </div>
                <div class="metric">
                    <span>Flags</span>
                    <span>${data.text_abuse_check.flags.length > 0 ? data.text_abuse_check.flags.join(', ') : 'None'}</span>
                </div>
                <div class="metric">
                    <span>AI Analysis</span>
                    <span>${data.text_abuse_check.ai_powered ? (data.text_abuse_check.ai_label + ' (' + (data.text_abuse_check.ai_confidence * 100).toFixed(1) + '%)') : 'Not Available'}</span>
                </div>
                <div class="metric">
                    <span>Description Length</span>
                    <span>${data.text_abuse_check.description_length || 0} chars</span>
                </div>
            </div>
            `;
            resultDiv.innerHTML = html;
        }
    </script>
</body>
</html>
    ''')

@app.route('/api/check_image', methods=['POST'])
def check_image_api():
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
            
        image_data = data['image']
        description = data.get('description', '')
        
        result = analyze_content(image_data, description)
        return jsonify(result)
        
    except Exception as e:
        error_msg = str(e)
        print(f"API Error: {error_msg}")
        traceback.print_exc()
        
        # Log to file so we can see it
        with open("backend_error.txt", "w") as f:
            f.write(f"Error: {error_msg}\n")
            f.write(traceback.format_exc())
            
        return jsonify({'error': error_msg}), 500


if __name__ == '__main__':
    print("🚀 Starting Working Demo Web App...")
    print("🌍 Open your browser at: http://localhost:5001")
    app.run(debug=True, port=5001, host='0.0.0.0')