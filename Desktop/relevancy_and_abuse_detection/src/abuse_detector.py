"""
Enhanced Abuse Detection Model - Detecting humans, weapons, flags, and inappropriate content in road images
Built from scratch without pre-trained models for final year project
"""

import os
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
from tqdm import tqdm
import pickle
import re
from typing import List, Dict, Tuple, Any
import logging

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *
from utils.helpers import load_and_preprocess_image, plot_training_history, plot_confusion_matrix

class AbuseDetector:
    """Enhanced Abuse Detection Model for road images - Built from scratch"""
    
    def __init__(self):
        self.model = None
        self.history = None
        self.class_names = ['non_abusive', 'abusive']
        self.model_path = ABUSE_MODEL_PATH
        
        # Initialize traditional computer vision detectors for specific content
        self.face_cascade = None
        self.skin_detector = None
        self.initialize_traditional_detectors()
        
        # Contextual text abuse detection categories
        self.abuse_categories = [
            'clean',           # No abuse
            'hate_speech',     # Hate speech, discrimination
            'harassment',      # Personal attacks, bullying
            'political_attack', # Political hate, divisive content
            'threat',          # Threats, violence
            'sexual_content'   # Sexual harassment, inappropriate
        ]
        
        # Initialize contextual text analysis
        self.contextual_text_model = None
        self.text_tokenizer = None
        self.initialize_contextual_text_detector()
        
        # Setup logging for contextual analysis
        self.setup_contextual_logging()
        
        # Initialize list to hold trained models
        self.trained_models = []
    
    def initialize_traditional_detectors(self):
        """Initialize traditional computer vision detectors (not pre-trained DL models)"""
        try:
            # Load OpenCV Haar cascade for face detection (traditional CV, not DL)
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                print("✓ Face detector initialized (traditional CV)")
            else:
                print("⚠ Face cascade not found, face detection disabled")
        except Exception as e:
            print(f"⚠ Traditional detector initialization failed: {e}")
    
    def setup_contextual_logging(self):
        """Setup logging for contextual text analysis"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def initialize_contextual_text_detector(self):
        """Initialize contextual text abuse detection system"""
        try:
            # Try to load pre-trained contextual model
            model_path = "models/contextual_abuse_detector"
            if os.path.exists(f"{model_path}/model.h5"):
                import pickle
                import json
                
                # Load model
                self.contextual_text_model = tf.keras.models.load_model(f"{model_path}/model.h5")
                
                # Load tokenizer
                with open(f"{model_path}/tokenizer.pkl", 'rb') as f:
                    self.text_tokenizer = pickle.load(f)
                
                # Load metadata
                with open(f"{model_path}/metadata.json", 'r') as f:
                    metadata = json.load(f)
                    self.contextual_categories = {int(k): v for k, v in metadata['categories'].items()}
                
                print("✅ Contextual text abuse detector loaded successfully")
            else:
                print("⚠️ Contextual text model not found. Use fallback keyword detection.")
                self.contextual_text_model = None
                self.text_tokenizer = None
        except Exception as e:
            print(f"⚠️ Failed to load contextual text model: {e}")
            self.contextual_text_model = None
            self.text_tokenizer = None
    
    def detect_contextual_text_abuse(self, text: str) -> Dict[str, Any]:
        """
        Advanced contextual text abuse detection
        Understands context and implicit meanings beyond simple keywords
        """
        
        if not text or not text.strip():
            return {
                'is_abusive': False,
                'category': 'clean',
                'confidence': 1.0,
                'method': 'empty_text'
            }
        
        # If we have the trained contextual model, use it
        if self.contextual_text_model and self.text_tokenizer:
            return self._predict_with_transformer(text)
        else:
            # Fallback to advanced pattern-based detection
            return self._detect_with_patterns(text)
    
    def _predict_with_transformer(self, text: str) -> Dict[str, Any]:
        """Use trained Tiny Transformer for contextual abuse detection"""
        try:
            from tensorflow.keras.preprocessing.sequence import pad_sequences
            
            # Tokenize and pad text
            sequence = self.text_tokenizer.texts_to_sequences([text])
            padded = pad_sequences(sequence, maxlen=100, padding='post', truncating='post')
            
            # Get prediction
            prediction = self.contextual_text_model.predict(padded, verbose=0)[0]
            predicted_class = int(np.argmax(prediction))
            confidence = float(prediction[predicted_class])
            
            # Get category name
            category = self.contextual_categories.get(predicted_class, 'unknown')
            
            # Analyze context patterns
            context_analysis = self._analyze_context_patterns(text)
            
            return {
                'is_abusive': predicted_class > 0,
                'category': category,
                'confidence': confidence,
                'severity_score': self._calculate_severity(predicted_class, confidence),
                'context_flags': context_analysis,
                'method': 'transformer',
                'reasoning': self._generate_reasoning(text, category, context_analysis)
            }
            
        except Exception as e:
            print(f"Error in transformer prediction: {e}")
            return self._detect_with_patterns(text)
    
    def _detect_with_patterns(self, text: str) -> Dict[str, Any]:
        """Fallback pattern-based contextual abuse detection"""
        
        text_lower = text.lower()
        context_analysis = self._analyze_context_patterns(text)
        
        # Check for different types of contextual abuse
        abuse_score = 0
        detected_category = 'clean'
        reasoning_parts = []
        
        # Political toxicity detection
        political_indicators = [
            r'(trump|biden|democrat|republican|liberal|conservative).*?(stupid|idiot|destroy|enemy|traitor)',
            r'(leftist|rightist|socialist|communist|fascist).*?(scum|moron|evil)',
            r'(snowflake|libtard|trumptard|sheep|sheeple)',
        ]
        
        for pattern in political_indicators:
            if re.search(pattern, text_lower, re.IGNORECASE):
                abuse_score += 0.7
                detected_category = 'political_toxicity'
                reasoning_parts.append('political attack language detected')
                break
        
        # Identity-based attacks
        identity_patterns = [
            r'(people like you|your kind|you people)',
            r'(go back to|belongs in|should stay in)',
            r'(typical|all|every).*(woman|man|black|white|muslim|christian|gay|straight)',
        ]
        
        for pattern in identity_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                abuse_score += 0.8
                detected_category = 'hate_speech'
                reasoning_parts.append('identity-based attack detected')
                break
        
        # Veiled threats
        threat_patterns = [
            r'(something bad|things happen|accidents occur|watch out|be careful)',
            r'(know where you|find you|get you|coming for you)',
            r'(deserve what|karma|payback|regret)',
        ]
        
        for pattern in threat_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                abuse_score += 0.9
                detected_category = 'threat_violence'
                reasoning_parts.append('veiled threat detected')
                break
        
        # Harassment patterns
        harassment_patterns = [
            r'(nobody likes|everyone hates|no one cares about) you',
            r'(kill yourself|end it|do us a favor)',
            r'(worthless|pathetic|loser|failure) (human|person|life)',
        ]
        
        for pattern in harassment_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                abuse_score += 0.8
                detected_category = 'harassment'
                reasoning_parts.append('harassment language detected')
                break
        
        # Sexual harassment patterns
        sexual_patterns = [
            r'(body|curves|tight|sexy).*?(road|street|pothole)',
            r'(private|bedroom|my place).*?(discuss|talk|meet)',
            r'(baby|sweetheart|honey).*?(construction|repair)',
        ]
        
        for pattern in sexual_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                abuse_score += 0.7
                detected_category = 'sexual_harassment'
                reasoning_parts.append('sexual harassment detected')
                break
        
        # Determine if abusive
        is_abusive = abuse_score > 0.5
        confidence = min(abuse_score, 1.0)
        
        if not reasoning_parts:
            reasoning_parts.append('contextual analysis of language patterns')
        
        return {
            'is_abusive': is_abusive,
            'category': detected_category,
            'confidence': confidence,
            'severity_score': abuse_score,
            'context_flags': context_analysis,
            'method': 'pattern_based',
            'reasoning': '; '.join(reasoning_parts)
        }
    
    def _analyze_context_patterns(self, text: str) -> Dict[str, bool]:
        """Analyze text for specific context patterns"""
        
        text_lower = text.lower()
        
        context_patterns = {
            'political_dogwhistles': [
                r'\b(trump|biden|liberal|conservative|democrat|republican)\b.*(stupid|idiot|moron|destroy|enemy|traitor)',
                r'(left|right).wing.*(nuts|crazy|terrorist|communist|fascist)',
                r'(snowflake|libtard|trumptard|sheep|sheeple)',
            ],
            'identity_attacks': [
                r'(people like you|your kind|you people)',
                r'(go back to|belongs in|should stay in)',
                r'(typical|all|every).*(woman|man|black|white|muslim|christian|gay|straight)',
            ],
            'veiled_threats': [
                r'(something bad|things happen|accidents occur|watch out|be careful)',
                r'(know where you|find you|get you|coming for you)',
                r'(deserve what|karma|payback|regret)',
            ],
            'harassment_patterns': [
                r'(nobody likes|everyone hates|no one cares about) you',
                r'(kill yourself|end it|do us a favor)',
                r'(worthless|pathetic|loser|failure) (human|person|life)',
            ]
        }
        
        flags = {}
        for pattern_type, patterns in context_patterns.items():
            flags[pattern_type] = any(
                re.search(pattern, text_lower, re.IGNORECASE) 
                for pattern in patterns
            )
        
        return flags
    
    def _calculate_severity(self, predicted_class: int, confidence: float) -> float:
        """Calculate abuse severity score"""
        if predicted_class == 0:  # Clean
            return 0.0
        
        # Weight by category severity
        severity_weights = {
            1: 0.8,  # hate_speech
            2: 0.6,  # harassment  
            3: 0.4,  # political_toxicity
            4: 0.9,  # threat_violence
            5: 0.7   # sexual_harassment
        }
        
        base_severity = severity_weights.get(predicted_class, 0.5)
        return base_severity * confidence
    
    def _generate_reasoning(self, text: str, category: str, context_flags: Dict[str, bool]) -> str:
        """Generate human-readable reasoning for classification"""
        
        if category == 'clean':
            return "Text appears to be clean road-related content without abusive language."
        
        reasons = [f"Classified as {category}"]
        
        if context_flags.get('political_dogwhistles'):
            reasons.append("contains political dog whistles or divisive language")
        
        if context_flags.get('identity_attacks'):
            reasons.append("contains language targeting identity groups")
        
        if context_flags.get('veiled_threats'):
            reasons.append("contains veiled threats or intimidation")
        
        if context_flags.get('harassment_patterns'):
            reasons.append("contains harassment or bullying language patterns")
        
        if len(reasons) == 1:
            reasons.append("based on contextual language patterns")
        
        return "; ".join(reasons)
    
    def extract_contextual_features(self, text: str) -> Dict[str, Any]:
        """
        Extract contextual features from text that indicate potential abuse
        This goes beyond simple keyword matching to understand context
        """
        features = {}
        text_lower = text.lower()
        
        # Political context indicators (words that can be neutral or abusive depending on context)
        political_terms = [
            'trump', 'biden', 'democrat', 'republican', 'liberal', 'conservative',
            'maga', 'socialist', 'communist', 'fascist', 'progressive', 'leftist', 'rightist'
        ]
        features['political_context'] = any(term in text_lower for term in political_terms)
        
        # Identity-based terms (can be abusive depending on context)
        identity_terms = [
            'immigrant', 'muslim', 'christian', 'jewish', 'black', 'white',
            'hispanic', 'latino', 'asian', 'gay', 'lesbian', 'transgender', 
            'woman', 'man', 'foreigner', 'native', 'citizen'
        ]
        features['identity_context'] = any(term in text_lower for term in identity_terms)
        
        # Negative sentiment indicators (when combined with other contexts, indicates abuse)
        negative_indicators = [
            'hate', 'destroy', 'ruin', 'terrible', 'awful', 'disgusting',
            'should be fired', 'incompetent', 'stupid', 'idiot', 'moron',
            'worthless', 'useless', 'pathetic', 'failure', 'scum'
        ]
        features['negative_sentiment'] = any(indicator in text_lower for indicator in negative_indicators)
        
        # Threat indicators (context suggesting violence or harm)
        threat_indicators = [
            'violence', 'burn', 'destroy', 'make them pay', 'teach a lesson',
            'take matters', 'force them', 'should be eliminated', 'get rid of',
            'someone should', 'need to be stopped', 'take action against'
        ]
        features['threat_context'] = any(indicator in text_lower for indicator in threat_indicators)
        
        # Sexual context indicators
        sexual_indicators = [
            'body', 'sexy', 'attractive', 'hot', 'equipment', 'harass',
            'inappropriate', 'checking out', 'nice legs', 'curves',
            'hooking up', 'sexual', 'bedroom', 'intimate'
        ]
        features['sexual_context'] = any(indicator in text_lower for indicator in sexual_indicators)
        
        # Escalation patterns (language that escalates situations)
        escalation_patterns = [
            'always', 'never', 'all of them', 'every single', 'completely',
            'totally', 'absolutely', 'constantly', 'forever', 'everywhere'
        ]
        features['escalation_language'] = any(pattern in text_lower for pattern in escalation_patterns)
        
        # Dehumanizing language
        dehumanizing_terms = [
            'animals', 'pests', 'vermin', 'parasites', 'disease', 'cancer',
            'plague', 'infestation', 'breed like', 'swarm', 'invade'
        ]
        features['dehumanizing_language'] = any(term in text_lower for term in dehumanizing_terms)
        
        return features
    
    def analyze_contextual_abuse(self, text: str) -> Dict[str, Any]:
        """
        Advanced contextual abuse analysis that understands nuanced language
        
        Examples:
        - "Trump supporters are destroying our roads" - Political attack
        - "Those immigrants don't deserve road repairs" - Hate speech  
        - "The mayor is completely incompetent" - Harassment
        - "Someone should teach that official a lesson" - Threat
        """
        context_features = self.extract_contextual_features(text)
        text_lower = text.lower()
        
        # Calculate abuse probability based on context combinations
        abuse_score = 0.0
        category = 'clean'
        explanation = "Text appears to be a legitimate road issue report."
        
        # Threat detection (highest priority)
        if context_features['threat_context']:
            abuse_score = 0.85
            category = 'threat'
            explanation = "Contains threatening language or suggestions of violence"
        
        # Sexual content detection
        elif context_features['sexual_context']:
            abuse_score = 0.80
            category = 'sexual_content'
            explanation = "Contains inappropriate sexual content or harassment"
        
        # Hate speech detection (identity + negative sentiment + dehumanizing)
        elif (context_features['identity_context'] and 
              context_features['negative_sentiment'] and
              context_features['dehumanizing_language']):
            abuse_score = 0.90
            category = 'hate_speech'
            explanation = "Contains dehumanizing language targeting specific groups"
        
        # Hate speech (identity + negative sentiment)
        elif context_features['identity_context'] and context_features['negative_sentiment']:
            abuse_score = 0.75
            category = 'hate_speech'
            explanation = "Contains negative language targeting specific groups or identities"
        
        # Political attack (political terms + negative sentiment + escalation)
        elif (context_features['political_context'] and 
              context_features['negative_sentiment'] and
              context_features['escalation_language']):
            abuse_score = 0.80
            category = 'political_attack'
            explanation = "Contains escalated political attack language"
        
        # Political attack (political terms + negative sentiment)
        elif context_features['political_context'] and context_features['negative_sentiment']:
            abuse_score = 0.70
            category = 'political_attack'
            explanation = "Contains politically charged language with negative sentiment"
        
        # Harassment (personal attacks without identity/political context)
        elif (context_features['negative_sentiment'] and 
              any(word in text_lower for word in ['idiot', 'moron', 'stupid', 'incompetent', 'worthless'])):
            abuse_score = 0.65
            category = 'harassment'
            explanation = "Contains personal attacks or derogatory language"
        
        # Context-specific examples for common tricky cases
        
        # Example: "Trump is here" vs "Trump supporters are ruining everything"
        if 'trump' in text_lower:
            if any(negative in text_lower for negative in ['ruin', 'destroy', 'terrible', 'awful', 'hate']):
                abuse_score = max(abuse_score, 0.70)
                category = 'political_attack'
                explanation = "Political figure mentioned in negative/divisive context"
            elif text_lower.strip() == 'trump is here':
                abuse_score = 0.0
                category = 'clean'
                explanation = "Neutral mention of political figure without negative context"
        
        # Example: Context-aware immigrant detection
        if 'immigrant' in text_lower:
            if any(negative in text_lower for negative in ['don\'t deserve', 'shouldn\'t get', 'ruin', 'destroy']):
                abuse_score = max(abuse_score, 0.80)
                category = 'hate_speech'
                explanation = "Discriminatory language against immigrants"
        
        # Confidence adjustment based on multiple indicators
        confidence = min(0.95, abuse_score)
        if sum(context_features.values()) >= 3:  # Multiple context indicators
            confidence = min(0.95, confidence + 0.10)
        
        return {
            'abuse_score': abuse_score,
            'category': category,
            'is_abusive': abuse_score > 0.5,
            'confidence': confidence,
            'context_features': context_features,
            'explanation': explanation,
            'severity': 'high' if abuse_score > 0.8 else 'medium' if abuse_score > 0.6 else 'low'
        }
    
    def detect_text_abuse(self, text: str) -> Dict[str, Any]:
        """
        Main method for detecting text abuse using contextual analysis
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with detailed analysis results
        """
        # Perform contextual analysis
        contextual_result = self.analyze_contextual_abuse(text)
        
        # Traditional keyword check as additional signal
        traditional_keywords = [
            'fuck', 'shit', 'damn', 'bitch', 'asshole', 'bastard',
            'kill', 'murder', 'rape', 'terrorist', 'nazi'
        ]
        has_explicit_keywords = any(keyword in text.lower() for keyword in traditional_keywords)
        
        # Combine contextual and traditional analysis
        final_score = contextual_result['abuse_score']
        
        if has_explicit_keywords:
            final_score = max(final_score, 0.85)
            if contextual_result['category'] == 'clean':
                contextual_result['category'] = 'harassment'
                contextual_result['explanation'] = "Contains explicit abusive language"
        
        # Final decision
        is_abusive = final_score > 0.5
        
        return {
            'is_abusive': is_abusive,
            'abuse_score': final_score,
            'category': contextual_result['category'],
            'confidence': contextual_result['confidence'],
            'severity': contextual_result['severity'],
            'explanation': contextual_result['explanation'],
            'context_analysis': contextual_result['context_features'],
            'has_explicit_keywords': has_explicit_keywords,
            'recommendation': 'reject' if is_abusive else 'approve'
        }
    
    def detect_human_features(self, image_path):
        """
        Detect human features using traditional computer vision (not pre-trained DL)
        Returns detailed information about detected humans
        """
        results = {
            'faces': {'detected': False, 'count': 0, 'confidence': 0.0},
            'skin': {'detected': False, 'percentage': 0.0},
            'human_shapes': {'detected': False, 'count': 0}
        }
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return results
            
            # Face detection using Haar cascades (traditional CV)
            if self.face_cascade is not None:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(30, 30)
                )
                
                if len(faces) > 0:
                    results['faces']['detected'] = True
                    results['faces']['count'] = len(faces)
                    results['faces']['confidence'] = min(1.0, len(faces) * 0.3)
            
            # Skin detection using HSV color space (traditional CV)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            skin_pixels = cv2.countNonZero(skin_mask)
            total_pixels = image.shape[0] * image.shape[1]
            skin_percentage = (skin_pixels / total_pixels) * 100
            
            if skin_percentage > 5.0:  # Threshold for significant skin detection
                results['skin']['detected'] = True
                results['skin']['percentage'] = skin_percentage
            
            # Human shape detection using contours (traditional CV)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            human_like_shapes = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Filter small contours
                    # Check aspect ratio (human-like shapes)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = h / w if w > 0 else 0
                    if 1.5 < aspect_ratio < 3.5:  # Human-like aspect ratio
                        human_like_shapes += 1
            
            if human_like_shapes > 0:
                results['human_shapes']['detected'] = True
                results['human_shapes']['count'] = human_like_shapes
                
        except Exception as e:
            print(f"Human feature detection error: {e}")
        
        return results
    
    def detect_weapons_flags(self, image_path):
        """
        Detect weapon-like and flag-like objects using traditional computer vision
        """
        results = {
            'weapons': {'detected': False, 'confidence': 0.0, 'type': ''},
            'flags': {'detected': False, 'confidence': 0.0, 'colors': []}
        }
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                return results
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Weapon detection using edge detection and shape analysis
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:
                    # Check for long, thin objects (potential weapons)
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
                    
                    if aspect_ratio > 4:  # Long, thin objects
                        results['weapons']['detected'] = True
                        results['weapons']['confidence'] = min(1.0, aspect_ratio / 10)
                        results['weapons']['type'] = 'elongated_object'
            
            # Flag detection using color analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define flag-like color ranges
            flag_colors = {
                'red': ([0, 120, 70], [10, 255, 255]),
                'blue': ([100, 150, 0], [140, 255, 255]),
                'green': ([40, 40, 40], [80, 255, 255]),
                'yellow': ([20, 100, 100], [30, 255, 255])
            }
            
            detected_colors = []
            for color_name, (lower, upper) in flag_colors.items():
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                color_pixels = cv2.countNonZero(mask)
                total_pixels = image.shape[0] * image.shape[1]
                color_percentage = (color_pixels / total_pixels) * 100
                
                if color_percentage > 10:  # Significant presence of flag-like colors
                    detected_colors.append(color_name)
            
            if len(detected_colors) >= 2:  # Multiple flag-like colors
                results['flags']['detected'] = True
                results['flags']['confidence'] = min(1.0, len(detected_colors) * 0.3)
                results['flags']['colors'] = detected_colors
                
        except Exception as e:
            print(f"Weapons/flags detection error: {e}")
        
        return results
        
    def create_model(self, input_shape=(224, 224, 3)):
        """Create the abuse detection model - Custom CNN from scratch"""
        print("Creating custom abuse detection CNN model from scratch...")
        
        # Build custom CNN architecture from scratch
        model = keras.Sequential([
            # Input layer
            layers.Input(shape=input_shape),
            
            # First Convolutional Block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.2),
            
            # Second Convolutional Block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.3),
            
            # Third Convolutional Block
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.3),
            
            # Fourth Convolutional Block
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.4),
            
            # Fifth Convolutional Block
            layers.Conv2D(512, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.5),
            
            # Dense layers
            layers.Dense(512, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.4),
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(1, activation='sigmoid')  # Binary classification
        ])
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=LEARNING_RATE),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        print("Custom abuse detection CNN model created successfully!")
        print(f"Total parameters: {model.count_params():,}")
        return model
    
    def create_data_generators(self, train_dir, val_dir):
        """Create data generators for training"""
        
        # Enhanced data augmentation for abuse detection
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=30,
            width_shift_range=0.3,
            height_shift_range=0.3,
            shear_range=0.3,
            zoom_range=0.3,
            horizontal_flip=True,
            vertical_flip=False,
            brightness_range=[0.7, 1.3],
            fill_mode='nearest'
        )
        
        # Only rescaling for validation
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        # Create generators
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='binary',
            shuffle=True
        )
        
        validation_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='binary',
            shuffle=False
        )
        
        return train_generator, validation_generator
    
    def detect_faces(self, image_path):
        """Detect faces in an image using basic computer vision"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return False, 0
            
            # Convert to RGB for face detection
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Simple face detection using Haar cascades (basic method)
            # This is a simplified approach - real implementation would use better models
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for skin-tone colored regions that might be faces
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define skin color range in HSV
            lower_skin = np.array([0, 20, 70])
            upper_skin = np.array([20, 255, 255])
            
            # Create mask for skin color
            skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # Find contours
            contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Check for face-like circular/oval regions
            face_count = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Minimum face area
                    # Check if contour is roughly circular (face-like)
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        if 0.3 < circularity < 1.2:  # Roughly circular
                            face_count += 1
            
            return face_count > 0, face_count
            
        except Exception as e:
            print(f"Error in face detection: {e}")
            return False, 0
    
    def detect_weapons(self, image_path):
        """Simple weapon detection using basic image analysis"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False, 0.0
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Look for dark, elongated objects (simplified weapon detection)
            # This is a basic implementation - real weapon detection needs more sophisticated models
            
            # Apply threshold to find dark objects
            _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            weapon_score = 0.0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Filter small objects
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w) / h
                    
                    # Check for elongated objects (potential weapons)
                    if aspect_ratio > 2.5 or aspect_ratio < 0.4:
                        weapon_score += 0.3
            
            has_weapon = weapon_score > 0.5
            return has_weapon, weapon_score
            
        except Exception as e:
            print(f"Error in weapon detection: {e}")
            return False, 0.0
    
    def detect_inappropriate_flags(self, image_path):
        """Detect flag-like patterns that might be inappropriate"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False, 0.0
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for common flag colors
            # Red range
            red_lower1 = np.array([0, 50, 50])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 50, 50])
            red_upper2 = np.array([180, 255, 255])
            
            # Create masks
            red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
            red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)
            
            # White range (for flag detection)
            white_lower = np.array([0, 0, 200])
            white_upper = np.array([180, 30, 255])
            white_mask = cv2.inRange(hsv, white_lower, white_upper)
            
            # Check for rectangular patterns (flags are usually rectangular)
            red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            flag_score = 0.0
            
            for contours in [red_contours, white_contours]:
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 1000:  # Filter small areas
                        # Approximate contour
                        epsilon = 0.02 * cv2.arcLength(contour, True)
                        approx = cv2.approxPolyDP(contour, epsilon, True)
                        
                        # Check if it's roughly rectangular (4 corners)
                        if len(approx) >= 4:
                            x, y, w, h = cv2.boundingRect(contour)
                            aspect_ratio = float(w) / h
                            
                            # Flags typically have certain aspect ratios
                            if 1.5 <= aspect_ratio <= 3.0:
                                flag_score += 0.4
            
            has_flag = flag_score > 0.6
            return has_flag, flag_score
            
        except Exception as e:
            print(f"Error in flag detection: {e}")
            return False, 0.0
    
    def comprehensive_abuse_check(self, image_path):
        """
        Enhanced comprehensive abuse detection combining multiple traditional CV methods
        This approach is built from scratch without using pre-trained models
        """
        
        # Check for human features (faces, skin, body shapes)
        human_results = self.detect_human_features(image_path)
        
        # Check for weapons and flags
        objects_results = self.detect_weapons_flags(image_path)
        
        # Combine all detection results
        abuse_indicators = {
            'faces': human_results['faces'],
            'skin': human_results['skin'],
            'human_shapes': human_results['human_shapes'],
            'weapons': objects_results['weapons'],
            'flags': objects_results['flags']
        }
        
        # Determine overall abuse status
        overall_abuse = (
            human_results['faces']['detected'] or
            human_results['skin']['detected'] or
            human_results['human_shapes']['detected'] or
            objects_results['weapons']['detected'] or
            objects_results['flags']['detected']
        )
        
        # Calculate confidence score based on detections
        confidence_scores = []
        
        if human_results['faces']['detected']:
            confidence_scores.append(human_results['faces']['confidence'])
        
        if human_results['skin']['detected']:
            # Convert skin percentage to confidence (higher percentage = higher confidence)
            skin_confidence = min(1.0, human_results['skin']['percentage'] / 20.0)
            confidence_scores.append(skin_confidence)
        
        if human_results['human_shapes']['detected']:
            # Convert shape count to confidence
            shape_confidence = min(1.0, human_results['human_shapes']['count'] * 0.2)
            confidence_scores.append(shape_confidence)
        
        if objects_results['weapons']['detected']:
            confidence_scores.append(objects_results['weapons']['confidence'])
        
        if objects_results['flags']['detected']:
            confidence_scores.append(objects_results['flags']['confidence'])
        
        # Overall confidence is the maximum of individual confidences
        overall_confidence = max(confidence_scores) if confidence_scores else 0.0
        
        # Add reasoning for the decision
        abuse_indicators['reasoning'] = []
        if human_results['faces']['detected']:
            abuse_indicators['reasoning'].append(f"Detected {human_results['faces']['count']} human face(s)")
        if human_results['skin']['detected']:
            abuse_indicators['reasoning'].append(f"Detected significant skin exposure ({human_results['skin']['percentage']:.1f}%)")
        if human_results['human_shapes']['detected']:
            abuse_indicators['reasoning'].append(f"Detected {human_results['human_shapes']['count']} human-like shape(s)")
        if objects_results['weapons']['detected']:
            abuse_indicators['reasoning'].append(f"Detected potential weapon ({objects_results['weapons']['type']})")
        if objects_results['flags']['detected']:
            abuse_indicators['reasoning'].append(f"Detected flag-like colors: {', '.join(objects_results['flags']['colors'])}")
        
        return overall_abuse, overall_confidence, abuse_indicators
    
    def train(self, train_dir=None, val_dir=None, epochs=EPOCHS):
        """Train the abuse detection model"""
        
        if train_dir is None:
            train_dir = os.path.join(PROCESSED_DATA_DIR, 'train')
        if val_dir is None:
            val_dir = os.path.join(PROCESSED_DATA_DIR, 'val')
        
        print(f"Training abuse detection model...")
        print(f"Train directory: {train_dir}")
        print(f"Validation directory: {val_dir}")
        
        # Check if directories exist
        if not os.path.exists(train_dir) or not os.path.exists(val_dir):
            print("Training directories not found. Please run data preparation first.")
            return None
        
        # Create model if not exists
        if self.model is None:
            self.create_model()
        
        # Create data generators
        train_generator, val_generator = self.create_data_generators(train_dir, val_dir)
        
        print(f"Found {train_generator.samples} training images")
        print(f"Found {val_generator.samples} validation images")
        print(f"Classes: {train_generator.class_indices}")
        
        # Define callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=7,
                min_lr=1e-8
            ),
            keras.callbacks.ModelCheckpoint(
                os.path.join(self.model_path, 'best_model.h5'),
                monitor='val_accuracy',
                save_best_only=True,
                save_weights_only=False
            )
        ]
        
        # Train the model
        steps_per_epoch = max(1, train_generator.samples // BATCH_SIZE)
        validation_steps = max(1, val_generator.samples // BATCH_SIZE)
        
        self.history = self.model.fit(
            train_generator,
            steps_per_epoch=steps_per_epoch,
            epochs=epochs,
            validation_data=val_generator,
            validation_steps=validation_steps,
            callbacks=callbacks,
            verbose=1
        )
        
        # Fine-tune the model
        print("\nFine-tuning the model...")
        self._fine_tune_model(train_generator, val_generator, epochs=15)
        
        # Save the model
        self.save_model()
        
        # Plot training history
        plot_training_history(self.history, "Abuse Detection")
        
        return self.history
    
    def _fine_tune_model(self, train_generator, val_generator, epochs=15):
        """Fine-tune the pre-trained layers"""
        
        # Unfreeze the top layers of the base model
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Fine-tune from this layer onwards
        fine_tune_at = 50
        
        # Freeze all the layers before fine_tune_at
        for layer in base_model.layers[:fine_tune_at]:
            layer.trainable = False
        
        # Use a lower learning rate for fine-tuning
        self.model.compile(
            optimizer=Adam(learning_rate=LEARNING_RATE/20),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        # Continue training
        fine_tune_epochs = epochs
        total_epochs = len(self.history.history['loss']) + fine_tune_epochs
        
        history_fine = self.model.fit(
            train_generator,
            steps_per_epoch=max(1, train_generator.samples // BATCH_SIZE),
            epochs=total_epochs,
            initial_epoch=len(self.history.history['loss']),
            validation_data=val_generator,
            validation_steps=max(1, val_generator.samples // BATCH_SIZE),
            verbose=1
        )
        
        # Merge histories
        for key in self.history.history.keys():
            self.history.history[key].extend(history_fine.history[key])
    
    def predict(self, image_path, use_comprehensive=True):
        """Predict if an image contains abusive content"""
        
        if use_comprehensive:
            # Use comprehensive multi-method approach
            is_abusive, confidence, details = self.comprehensive_abuse_check(image_path)
            
            if is_abusive:
                predicted_class = 'abusive'
                return predicted_class, confidence, details
        
        # Use trained model if available
        if self.model is None:
            if not self.load_model():
                # Fallback to comprehensive check only
                is_abusive, confidence, details = self.comprehensive_abuse_check(image_path)
                predicted_class = 'abusive' if is_abusive else 'non_abusive'
                return predicted_class, confidence, details
        
        # Preprocess image for model
        image = load_and_preprocess_image(image_path)
        if image is None:
            return 'error', 0.0, {}
        
        # Make prediction with model
        image_batch = np.expand_dims(image, axis=0)
        prediction = self.model.predict(image_batch, verbose=0)
        model_confidence = float(prediction[0][0])
        
        # Combine with comprehensive check
        is_abusive_comp, comp_confidence, details = self.comprehensive_abuse_check(image_path)
        
        # Combine results (weighted average)
        final_confidence = (model_confidence * 0.7) + (comp_confidence * 0.3)
        
        if final_confidence > 0.5 or is_abusive_comp:
            predicted_class = 'abusive'
        else:
            predicted_class = 'non_abusive'
            final_confidence = 1 - final_confidence
        
        return predicted_class, final_confidence, details
    
    def evaluate(self, test_dir=None):
        """Evaluate the model on test data"""
        
        if test_dir is None:
            test_dir = os.path.join(PROCESSED_DATA_DIR, 'test')
        
        if not os.path.exists(test_dir):
            print("Test directory not found.")
            return None
        
        # Create test data generator
        test_datagen = ImageDataGenerator(rescale=1./255)
        test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=IMAGE_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='binary',
            shuffle=False
        )
        
        print(f"Evaluating on {test_generator.samples} test images...")
        
        if self.model is not None:
            # Evaluate with model
            test_loss, test_accuracy, test_precision, test_recall = self.model.evaluate(test_generator, verbose=1)
            print(f"Test Accuracy: {test_accuracy:.4f}")
            print(f"Test Precision: {test_precision:.4f}")
            print(f"Test Recall: {test_recall:.4f}")
            print(f"Test Loss: {test_loss:.4f}")
            
            # Get predictions
            predictions = self.model.predict(test_generator, verbose=1)
            predicted_classes = (predictions > 0.5).astype(int).flatten()
            true_classes = test_generator.classes
            
            # Plot confusion matrix
            plot_confusion_matrix(true_classes, predicted_classes, 
                                self.class_names, "Abuse Detection")
            
            return test_accuracy, test_loss
        else:
            print("No trained model available for evaluation.")
            return None, None
    
    def save_model(self):
        """Save the trained model"""
        if self.model is None:
            print("No model to save")
            return
        
        # Save the full model
        model_file = os.path.join(self.model_path, 'abuse_model.h5')
        self.model.save(model_file)
        
        # Save training history
        history_file = os.path.join(self.model_path, 'training_history.pkl')
        with open(history_file, 'wb') as f:
            pickle.dump(self.history.history if self.history else {}, f)
        
        print(f"Abuse detection model saved to {model_file}")
    
    def load_model(self):
        """Load a trained model"""
        model_file = os.path.join(self.model_path, 'abuse_model.h5')
        
        if os.path.exists(model_file):
            self.model = keras.models.load_model(model_file)
            print(f"Abuse detection model loaded from {model_file}")
            
            # Load training history if available
            history_file = os.path.join(self.model_path, 'training_history.pkl')
            if os.path.exists(history_file):
                with open(history_file, 'rb') as f:
                    history_dict = pickle.load(f)
                    # Create a mock history object
                    class MockHistory:
                        def __init__(self, history_dict):
                            self.history = history_dict
                    self.history = MockHistory(history_dict)
            
            return True
        else:
            print(f"No saved abuse detection model found at {model_file}")
            return False
    
    def load_trained_models(self, model_paths):
        """Load trained models from specified paths"""
        self.trained_models = []
        for path in model_paths:
            if os.path.exists(path):
                model = tf.keras.models.load_model(path)
                self.trained_models.append(model)
                print(f"✅ Loaded model from {path}")
            else:
                print(f"❌ Model not found at {path}")

    def predict_with_all_models(self, image):
        """Generate predictions using all trained models"""
        predictions = []
        for model in self.trained_models:
            prediction = model.predict(image)
            predictions.append(prediction)
        return predictions

# Update RelevancyDetector to load trained models
class RelevancyDetector:
    def load_trained_models(self, model_paths):
        """Load trained models from specified paths"""
        self.trained_models = []
        for path in model_paths:
            if os.path.exists(path):
                model = tf.keras.models.load_model(path)
                self.trained_models.append(model)
                print(f"✅ Loaded model from {path}")
            else:
                print(f"❌ Model not found at {path}")

    def predict_with_all_models(self, image):
        """Generate predictions using all trained models"""
        predictions = []
        for model in self.trained_models:
            prediction = model.predict(image)
            predictions.append(prediction)
        return predictions

def main():
    """Main function for training the abuse detection model"""
    
    print("=== Abuse Detection Model ===\n")
    
    # Create detector
    detector = AbuseDetector()
    
    # Check if trained model exists
    if detector.load_model():
        print("Loaded existing abuse detection model.")
        
        # Evaluate if test data exists
        test_dir = os.path.join(PROCESSED_DATA_DIR, 'test')
        if os.path.exists(test_dir):
            detector.evaluate()
    else:
        print("Training new abuse detection model...")
        
        # Train the model
        history = detector.train()
        
        if history:
            print("Training completed successfully!")
            
            # Evaluate the model
            detector.evaluate()
        else:
            print("Training failed. Please check your data directories.")
    
    # Test prediction on sample images
    sample_dir = os.path.join('data', 'sample')
    if os.path.exists(sample_dir):
        print(f"\nTesting abuse detection on sample images...")
        
        sample_images = [f for f in os.listdir(sample_dir) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for image_name in sample_images:
            image_path = os.path.join(sample_dir, image_name)
            predicted_class, confidence, details = detector.predict(image_path)
            print(f"{image_name}: {predicted_class} ({confidence:.2f})")
            print(f"  Details: {details}")

if __name__ == "__main__":
    main()
