"""
Configuration file for the Road Issues Detection System
"""

import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
SAMPLE_DATA_DIR = os.path.join(DATA_DIR, 'sample')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Model paths
RELEVANCY_MODEL_PATH = os.path.join(MODELS_DIR, 'relevancy_model')
ABUSE_MODEL_PATH = os.path.join(MODELS_DIR, 'abuse_model')
TEXT_MODEL_PATH = os.path.join(MODELS_DIR, 'text_model')

# Image settings
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB max file size

# Model training parameters
EPOCHS = 50
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.2
TEST_SPLIT = 0.1

# 4 Image Classes - Exactly as requested
IMAGE_CLASSES = {
    0: 'relevant',              # Road images (clean)
    1: 'irrelevant',            # Non-road images (clean)
    2: 'relevant_abusive',      # Road images with inappropriate content
    3: 'irrelevant_abusive'     # Non-road images with inappropriate content
}

# 2 Text Classes - Exactly as requested  
TEXT_CLASSES = {
    0: 'clean',      # Clean, appropriate text
    1: 'abusive'     # Inappropriate, abusive text
}

# Legacy compatibility for existing code
RELEVANCY_CLASSES = {
    0: 'irrelevant',  # Non-road images
    1: 'relevant'     # Road images
}

ABUSE_CLASSES = {
    0: 'non_abusive',  # Clean images
    1: 'abusive'       # Images with inappropriate content
}

# Text filtering settings
ABUSIVE_KEYWORDS = [
    # Profanity
    'fuck', 'shit', 'damn', 'bastard', 'bitch', 'asshole',
    # Hate speech
    'racist', 'nazi', 'terrorist', 'kill', 'murder', 'bomb',
    # Inappropriate content
    'porn', 'sex', 'nude', 'naked', 'drugs', 'cocaine', 'marijuana',
    # Threats
    'threat', 'violence', 'attack', 'destroy', 'harm'
]

# Web app settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RELEVANCY_MODEL_PATH, exist_ok=True)
os.makedirs(ABUSE_MODEL_PATH, exist_ok=True)
os.makedirs(TEXT_MODEL_PATH, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
