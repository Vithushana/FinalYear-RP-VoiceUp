AI Authenticity and Garbage Detection – VITHUSHANA (IT22922298)

AI Authenticity and Garbage Detection is the AI verification and image understanding module for the VoiceUp platform, developed by VITHUSHANA (IT22922298).

This component is responsible for:

AI vs Real image detection – checking whether a road-related image is a real camera photo or an AI-generated image.

Garbage detection with bounding boxes – detecting and localising garbage regions in images, for both single images and sets of images.

It ensures that:

Fake / AI-generated images are not misused as real evidence.

Only relevant road and garbage images are sent forward in the VoiceUp pipeline.

Garbage complaints are supported with clear, localised visual evidence.

🌍 Overall Project – VoiceUp

VoiceUp is an intelligent local issue reporting platform that empowers citizens to report community problems across multiple sectors while ensuring content quality through AI-powered validation.

The system uses advanced machine learning models to:

validate uploaded content,

detect abusive or fake inputs,

protect privacy, and

improve the reliability of reported issues.

Currently, VoiceUp supports Road Issues and Garbage Management with plans to expand to more community sectors.

This module, AI Authenticity and Garbage Detection – VITHUSHANA (IT22922298), works together with other validation components (such as abuse filtration and privacy protection) to strengthen the platform’s trustworthiness.

📋 Table of Contents

Overview

Key Functionalities

Technologies Used

AI Models & Performance

Installation & Setup

Running the Service

API Documentation

Configuration

Performance Metrics

Project Structure

Repository Location

Integration with VoiceUp

Key Achievements

VoiceUp System Overview

🎯 Overview

The AI Authenticity and Garbage Detection component acts as a specialised AI layer in the VoiceUp content validation pipeline.

It mainly focuses on two tasks:

Authenticity Validation (AI vs Real):
Verifies whether a road-related image is genuinely captured from the real world or generated/edited by AI tools.

Garbage Detection with Bounding Boxes:
Detects garbage in images and draws bounding boxes around the garbage regions. Supports both single-image and set-of-images processing.

Role in VoiceUp Ecosystem

Authenticity Gate: First layer for road images to ensure they are real before being accepted as evidence.

Garbage Visual Proof: Provides clear localisation of garbage in user-submitted photos.

Support Module: Works alongside privacy, abuse, and text-analysis components used in VoiceUp.

Developer Information

Component: AI Authenticity and Garbage Detection

Developer: VITHUSHANA

Student ID: IT22922298

Example Service Port: 5002

Sectors Supported: Road Issues, Garbage Issues

🔧 Key Functionalities
1️⃣ AI vs Real Road Image Classification

This sub-module verifies whether a road-related image is:

AI-generated / manipulated (ai), or

A real camera image (real).

Key points:

Designed specifically for road-related content (potholes, cracks, road surfaces, etc.).

Trained on 6000+ images (AI + real road images).

Uses a fine-tuned ResNet-50 as a binary classifier (ai, real).

Behaviour in the pipeline:

When the user reports a Road Issue:

The image is sent to this classifier.

If prediction = REAL with high confidence → the system can accept the report as authentic evidence.

If prediction = AI with high confidence → the report can be rejected, flagged, or queued for manual review.

2️⃣ Garbage Detection with Bounding Boxes

This sub-module detects garbage presence in images and draws bounding boxes around relevant regions.

Capabilities:

Works on:

Single image – live user complaint.

Multiple images / folder – batch evaluation or dataset processing.

For each image, it:

Detects garbage objects.

Returns class label (e.g., garbage / clean or more detailed types in the future).

Outputs bounding box coordinates and confidence score.

This helps:

Visualise exact regions where garbage is present.

Support analytics and clean-up planning in the garbage management sector.

3️⃣ Future Extension – Garbage Type Classification

As a future enhancement, this module can be extended to classify garbage types, for example:

plastic, glass, paper, cardboard, metal, etc.

This will support:

better environmental analytics,

data for municipal decision-making,

and integration with smart waste management systems.

🛠️ Technologies Used
AI / ML Frameworks

PyTorch – Deep learning framework.

Torchvision ResNet-50 – Backbone CNN for AI vs Real classification.

Object Detection Framework (e.g., YOLO-style or custom detector) – for garbage detection and bounding boxes.

scikit-learn – For precision, recall, F1-score, and confusion matrix.

Pillow (PIL) – Image loading and preprocessing.

NumPy – Numerical operations.

Matplotlib – Training curves and automatic PDF report creation.

Backend Technologies (optional if exposed as microservice)

Flask / FastAPI – REST API endpoints for validation.

Python 3.10+ – Core programming language.

🤖 AI Models & Performance
1. AI vs Real Image Classifier (ResNet-50)

Architecture: ResNet-50 (ImageNet-pretrained, fine-tuned on custom road dataset).

Task: Classify images into ai or real.

Dataset: 6000+ labelled road-related images (AI and real).

Train/Val/Test split: e.g., 70% train / 15% validation / 15% test.

Sample Final Test Results:

=== Test Results ===
Test Loss: 0.0596
Test Accuracy : 0.9789

Classification Report:
               precision    recall  f1-score   support

          ai       0.96      0.99      0.98      1089
        real       0.99      0.97      0.98      1276

    accuracy                           0.98      2365
   macro avg       0.98      0.98      0.98      2365
weighted avg       0.98      0.98      0.98      2365

Confusion Matrix:
[[1080    9]
 [  41 1235]]


Interpretation (simple):

Out of 2365 test images, only 50 are misclassified.

Both classes (ai and real) achieve very high precision (≥ 0.96) and recall (≥ 0.97).

The model is suitable as an automatic authenticity filter for road evidence images.

2. Garbage Detection Model

Type: Object Detection Model

Task: Detect and localise garbage regions using bounding boxes.

Output for each detection:

Class label (e.g., garbage / clean or detailed class),

Confidence value,

Bounding box coordinates [x_min, y_min, x_max, y_max].

When the dataset and final model are fully stabilised, mAP, precision, recall and class-wise metrics can be added here.

🚀 Installation & Setup
Prerequisites
Python 3.10+
pip install -r requirements.txt

Example Dependencies
torch
torchvision
numpy
Pillow
scikit-learn
matplotlib
flask          # if using REST API

▶️ Running the Service
1. Training the AI vs Real Classifier
cd component_vithushana       # adjust to actual folder name
python train_resnet50_ai_vs_real.py


This will:

Train the ResNet-50 classifier on the ai vs real dataset.

Save:

models/resnet50_ai_vs_real.pth – model weights.

results/training_history.csv – per-epoch metrics.

results/report.pdf – full training report (accuracy, loss, confusion matrix).

2. Running Single Image Prediction (CLI)
python predict.py test_images/real1.jpg


Example output:

Using device: cpu

Prediction: REAL (confidence: 1.00)
➡ This image is likely a REAL camera photo.


The same script can be used inside the VoiceUp backend to validate road images automatically.

3. Running Garbage Detection (Example)
python detect_garbage.py images/test_garbage.jpg


Output (conceptual):

images/test_garbage.jpg
 -> garbage (0.92) bbox=[100, 60, 250, 220]


Optionally, an annotated image with bounding boxes can be saved for visualisation.

4. Running as a Microservice
python ai_authenticity_garbage_service.py


Example endpoints (can be adjusted):

http://localhost:5002/ai-vs-real

http://localhost:5002/detect-garbage

📡 API Documentation (Example Design)
1. AI vs Real Endpoint

POST /ai-vs-real

Request Body:

{
  "image": "base64_encoded_image_string"
}


Response:

{
  "label": "REAL",
  "confidence": 0.98
}

2. Garbage Detection Endpoint

POST /detect-garbage

Request Body:

{
  "image": "base64_encoded_image_string",
  "mode": "single"   // or "batch" (optional)
}


Response Example:

{
  "detections": [
    {
      "class": "garbage",
      "confidence": 0.92,
      "bbox": [100, 60, 250, 220]
    }
  ],
  "has_garbage": true
}

⚙️ Configuration

Example configuration file config.ini:

[AI_VS_REAL]
model_path = models/resnet50_ai_vs_real.pth
threshold = 0.5

[GARBAGE_DETECTION]
model_path = models/garbage_detection_model.pth
confidence_threshold = 0.5

[SERVER]
port = 5002
debug = False
device = cuda

📊 Performance Metrics
AI vs Real Classifier (ResNet-50)

Accuracy: ~97.89%

Precision (AI): 0.96

Recall (AI): 0.99

Precision (REAL): 0.99

Recall (REAL): 0.97

These values show that the model performs strongly on both classes and is able to filter AI-generated images with high reliability.

Additional metrics (e.g., garbage detection mAP, inference latency, average processing time) can be reported based on final experiments.

📁 Project Structure
component_vithushana/
├── train_resnet50_ai_vs_real.py     # Training script (AI vs Real)
├── predict.py                       # Single-image prediction for AI vs Real
├── detect_garbage.py                # Garbage detection with bounding boxes
├── ai_authenticity_garbage_service.py  # Optional REST API microservice
├── models/
│   ├── resnet50_ai_vs_real.pth      # Trained AI vs Real model
│   └── garbage_detection_model.pth  # Trained garbage detection model
├── results/
│   ├── training_history.csv         # Training logs for AI vs Real
│   └── report.pdf                   # PDF report (curves + metrics)
├── data/
│   └── dataset/
│       ├── train/
│       │   ├── ai/
│       │   └── real/
│       ├── val/
│       │   ├── ai/
│       │   └── real/
│       └── test/
│           ├── ai/
│           └── real/
└── README.md                        # This documentation

🔗 Repository Location
GitHub Repository

Main Repository: https://github.com/Vithushana/FinalYear-RP-VoiceUp

Main Branch: main

Component Folder (example): /component_vithushana/

Local Folder Path (example)

Windows:
C:\Users\Admin pc\Desktop\FinalYear-RP-VoiceUp\component_vithushana\

README File:
C:\Users\Admin pc\Desktop\FinalYear-RP-VoiceUp\component_vithushana\README.md

(Folder and branch names can be adjusted to match the actual repository structure.)

🔗 Integration with VoiceUp
Upstream Services

Flutter App:
Sends road and garbage issue images to the main backend.

Main Backend (Port 5000):
Forwards relevant images to this AI Authenticity and Garbage Detection component for validation.

Downstream Dependencies

Main Database:
Stores the final validated complaints and system decisions.

Notification System:
Notifies users if their complaint is accepted, rejected, or needs revision (e.g., fake/AI image detected).

Communication Flow

User submits an issue (Road / Garbage) with an image through the app.

Main backend sends the image to this component.

This component:

Runs AI vs Real classification for road issues.

Runs garbage detection for garbage issues.

Returns a structured response with:

Predicted label(s),

Confidence scores,

Optional bounding box data.

Backend combines this result with other validation modules and decides whether to accept or reject the submission.

🎯 Key Achievements
Technical Achievements

Designed and implemented a ResNet-50–based AI vs Real classifier with ~97.89% test accuracy on a 6000+ image dataset.

Implemented support for single-image and batch garbage detection with bounding boxes.

Built a training pipeline that automatically generates:

CSV logs (training_history.csv)

A PDF report (report.pdf) including loss curves, accuracy curves, and confusion matrix.

Contribution to VoiceUp

Prevents AI-generated or fake images from being treated as real evidence for road issues.

Provides clear visual localisation of garbage to support garbage management decisions.

Designed to be modular, so it can be extended to other sectors or integrated with more models in the future.

📊 VoiceUp System Overview
VoiceUp Platform
├── Frontend Applications
│   ├── Flutter Mobile App (Android/iOS)
│   ├── Flutter Web App
│   └── React Landing Page
├── Backend Services
│   ├── Main Backend (Port 5000)
│   │   ├── User Management
│   │   ├── Post Management
│   │   └── Notification System
│   └── AI Validation Components
│       ├── Relevance and Abuse Filtration (Port 5001)
│       └── AI Authenticity and Garbage Detection (Port 5002) – VITHUSHANA
└── Database & Storage
    ├── PostgreSQL Database
    └── Image Storage


AI Authenticity and Garbage Detection – VITHUSHANA (IT22922298) is a core part of the VoiceUp validation stack, ensuring that uploaded images are authentic, relevant, and clearly interpretable for both road and garbage issues.