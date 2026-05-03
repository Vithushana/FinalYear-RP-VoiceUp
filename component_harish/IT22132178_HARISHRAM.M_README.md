# Relevance and Abuse Filtration - Harishram.M (IT22132178)

**Relevance and Abuse Filtration** is the core AI validation service for the VoiceUp platform, developed by Harishram.M (IT22132178). This component is responsible for content moderation, privacy protection, abuse detection, and relevance validation across multiple sectors. It ensures all user submissions meet community guidelines while protecting user privacy. Currently supporting **Road Issues** and **Garbage Management** sectors with the capability to expand to all community service areas.

OVERALL PROJECT: 
**VoiceUp** is an intelligent local issue reporting platform that empowers citizens to report community problems across multiple sectors while ensuring content quality through AI-powered moderation. The system uses advanced machine learning models to validate submissions, detect abuse, and protect user privacy. Currently supporting **Road Issues** and **Garbage Management** sectors with plans to expand to all community service areas.


---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Functionalities](#-key-functionalities)
- [Technologies Used](#-technologies-used)
- [AI Models & Performance](#-ai-models--performance)
- [Installation & Setup](#-installation--setup)
- [Running the Service](#-running-the-service)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Performance Metrics](#-performance-metrics)
- [Project Structure](#-project-structure)

---

## 🎯 Overview

The Relevance and Abuse Filter serves as the first line of defense in the VoiceUp content validation pipeline. It processes user submissions (images + text) and performs comprehensive validation checks before content reaches the main platform. The component operates as an independent microservice on port 5001 and handles both road and garbage issue types.

### **Role in VoiceUp Ecosystem:**
- **Primary Validator**: First checkpoint for all user submissions
- **Privacy Guardian**: Protects user identities through human detection
- **Content Quality Gate**: Ensures relevant, appropriate content
- **Strike System Enforcer**: Manages user violations with progressive warnings

### **Developer Information:**
- **Component**: Relevance and Abuse Filtration
- **Developer**: Harishram.M
- **Student ID**: IT22132178
- **Service Port**: 5001
- **Sectors Supported**: Road Issues, Garbage Issues

---

## 🔧 Key Functionalities

### **1. Privacy Protection**
- **Human Detection**: YOLOv8 model detects persons and faces with 90.6% accuracy
- **Realism Checks**: Distinguishes real humans from icons/cartoons using texture analysis
- **Face Protection**: Specialized detection for facial features
- **Privacy-First**: Automatically blocks content with identifiable humans
- **Detected Classes**: person, face

### **2. Content Relevance Validation**
- **Road Relevance Detection**: YOLOv8 model validates road-related content (94.2% accuracy)
- **Damage Classification**: Detects potholes, cracks, and road damage
- **Context Understanding**: Analyzes image context for relevance
- **Sector-Specific Validation**: Separate models for road and garbage issues
- **Detected Classes**: road, pothole, crack, pavement, asphalt

### **3. Garbage Relevance Validation**
- **Garbage Relevance Detection**: YOLOv8 model validates garbage-related content (92.8% accuracy)
- **Waste Classification**: Identifies garbage accumulation and illegal dumping
- **Cleanliness Assessment**: Evaluates environmental cleanliness
- **Context Analysis**: Detects garbage in road/public areas
- **Sector-Specific Processing**: Dedicated garbage issue validation
- **Detected Classes**: Clean, Garbage Detected

### **4. Abuse Detection**
- **Weapon Detection**: Identifies weapons, knives, and dangerous objects
- **Violence Detection**: Detects violent and aggressive content
- **Blood Detection**: Identifies blood and gore content
- **Default Content**: Flags inappropriate default imagery
- **Abusive Content**: Detects adult or harmful material
- **YOLOv8 Model**: Single comprehensive abuse detection system (76.8% accuracy)
- **Detected Classes**: weapons, blood, violence, default, abusive content

### **5. Text Abuse Detection**
- **DistilBERT Model**: Advanced NLP for text analysis (89.5% F1-Score)
- **Abusive Language**: Detects profanity, hate speech, and threats
- **Sarcasm Detection**: Identifies sarcastic and context-based abuse
- **Political Content**: Flags politically sensitive language
- **50K+ Training Samples**: Comprehensive vocabulary coverage
- **Detected Classes**: SAFE, ABUSE, SARCASM, POLITICAL

### **6. Strike Management System**
- **Progressive Warnings**: Warning → Strike 1 → Strike 2 → Strike 3
- **Dual Notifications**: Post rejection + strike warning alerts
- **User Tracking**: Maintains violation history per user
- **Smart Thresholds**: Context-aware violation assessment

---

## 🛠️ Technologies Used

### **AI/ML Frameworks**
- **YOLOv8**: Object detection for privacy, relevance, and abuse detection
- **DistilBERT**: Text analysis and abuse detection
- **OpenCV**: Image processing and feature extraction
- **PyTorch**: Deep learning model backend
- **Ultralytics**: YOLO model training and inference

### **Backend Technologies**
- **Flask**: Web framework for REST API
- **Python 3.8+**: Core programming language
- **NumPy**: Numerical computations
- **PIL/Pillow**: Image processing
- **Threading**: Parallel processing capabilities

### **Model Architecture**
- **5 Main AI Models**: Road Relevance, Garbage Relevance, Abuse Detection, Privacy Protection, Text Analysis
- **Confidence Thresholding**: Adaptive confidence management for each model
- **Real-time Processing**: Sub-2.3-second validation time
- **Sector-Specific Processing**: Separate validation for road and garbage issues

---

## 🤖 AI Models & Performance

### **1. Road Relevance Detection System**

**Architecture**: YOLOv8 Road Detection Model
**Accuracy**: 94.2% on validation set
**Model**: Single YOLOv8 model trained on road dataset
**Confidence threshold**: 50%

**What it detects**:
- ✅ Potholes, cracks, road damage
- ✅ Asphalt, concrete surfaces
- ✅ Road markings, lanes
- ❌ Documents, screenshots
- ❌ Indoor scenes, unrelated objects

### **2. Garbage Relevance Detection System**

**Architecture**: YOLOv8 Garbage Classification Model
**Accuracy**: 92.8% on validation set
**Model**: Single YOLOv8 model trained on garbage dataset
**Confidence threshold**: 75%

**What it detects**:
- ✅ Garbage and waste on roads
- ✅ Clean road surfaces
- ✅ Environmental cleanliness
- ❌ Non-road garbage scenarios

### **3. Abuse Detection System**

**Architecture**: YOLOv8 Abuse Detection Model
**Accuracy**: 76.8% on validation set
**Model**: Single YOLOv8 model trained on abuse dataset
**Confidence threshold**: 50%

**Detected Classes**:
- Weapons (guns, knives)
- Violence (fighting, blood)
- Blood (gore, injuries)
- Default (inappropriate default imagery)
- Abusive content (explicit imagery)

**Thresholds**:
- Weapons: 45% confidence
- Violence: 60% confidence
- Blood: 65% confidence
- Default: 50% confidence
- Abusive content: 55% confidence

### **4. Privacy Protection System**

**Architecture**: YOLOv8 Human Detection Model
**Accuracy**: 90.6% mAP50
**Model**: Single YOLOv8 model trained on human dataset
**Confidence threshold**: 45%

**Detected Classes**:
- Person (full body detection)
- Face (facial feature detection)

**Features**:
- Realism checks (distinguishes icons from real people)
- Size filtering (ignores tiny/distant people)

### **5. Text Abuse Detection System**

**Architecture**: DistilBERT Transformer Model
**Accuracy**: 89.5% F1-Score on validation set
**Model**: Fine-tuned DistilBERT for text classification
**Confidence threshold**: 50%

**Detected Classes**:
- SAFE (appropriate content)
- ABUSE (profanity, hate speech)
- SARCASM (context-based abuse)
- POLITICAL (politically sensitive language)

**Features**:
- Context understanding
- Sarcasm detection
- 50K+ training samples
- Comprehensive vocabulary coverage

---

## 🚀 Installation & Setup

### **Prerequisites**
```bash
Python 3.8+
pip install -r requirements.txt
```

### **Required Dependencies**
```bash
flask==2.3.3
ultralytics==8.0.196
torch>=1.9.0
torchvision>=0.10.0
opencv-python==4.8.1.78
numpy==1.24.3
Pillow==10.0.0
transformers==4.30.0
```

### **Model Setup**
1. Download trained models to `models/` directory:
   - `models/abuse_detection_final/abuse_detection_best.pt`
   - `models/human_detection_final/human_detection_best.pt`
   - `models/garbage_classification_model/best.pt`
   - `models/road_detection_model/road_detection_best.pt`
   - `models/text_abuse_model/` (DistilBERT files)

2. Ensure model configuration:
   ```bash
   models/trained_models_config.txt
   ```

---

## ▶️ Running the Service

### **Option 1: Direct Execution**
```bash
cd component_harish
python component_service.py
```

### **Option 2: Via Main Launcher**
```bash
cd ..
start_all_validation_services.bat
```

### **Service Endpoints**
- **Main Service**: `http://localhost:5001`
- **Health Check**: `http://localhost:5001/health`
- **Analysis Endpoint**: `http://localhost:5001/analyze`

### **Expected Output**
```
🤖 Loading Abuse Detection Models...
✅ Abuse detection models loaded successfully
🛡️ Loading Human Detection Model...
✅ Human detection model loaded successfully
🚦 Loading Road Detection Models...
✅ Road detection models loaded successfully
🗑️ Loading Garbage Classification Model...
✅ Garbage classification model loaded successfully
🧠 Loading Text Analysis Model...
✅ Text analysis model loaded successfully
🚀 Component 1 (Harish) starting on http://localhost:5001
```

---

## 📡 API Documentation

### **Main Analysis Endpoint**
**POST** `/analyze`

**Request Body:**
```json
{
    "image": "base64_encoded_image_string",
    "description": "User provided text description",
    "issue_type": "road" | "garbage"
}
```

**Response Structure:**
```json
{
    "flutter_response": {
        "success": true,
        "can_proceed": true,
        "title": "Validation Result",
        "message": "Content approved",
        "detailed_explanation": "Detailed analysis",
        "what_to_do_next": "Next steps"
    },
    "final_decision": {
        "status": "ACCEPTED",
        "accepted": true,
        "reason": "Content meets guidelines",
        "strike_issued": false
    },
    "strike_warning": {
        "has_strike": false,
        "strike_count": 0,
        "title": "No Violation",
        "message": "Content is appropriate"
    },
    "strike_notification": {
        "should_send": false,
        "title": "",
        "message": "",
        "strike_count": 0
    },
    "privacy_protection": {
        "humans_detected": false,
        "confidence": 0.99,
        "reason": "No humans detected"
    },
    "image_abuse_check": {
        "detected": false,
        "flags": [],
        "confidence": 0.95
    },
    "text_abuse_check": {
        "detected": false,
        "flags": [],
        "confidence": 0.92
    },
    "garbage_classification": {
        "status": "clean",
        "confidence": 0.88
    }
}
```

---

## ⚙️ Configuration

### **Model Configuration** (`models/trained_models_config.txt`)
```ini
[ABUSE_DETECTION]
model_path = models/abuse_detection_final/abuse_detection_best.pt
confidence_threshold = 0.5

[HUMAN_DETECTION]
model_path = models/human_detection_final/human_detection_best.pt
confidence_threshold = 0.45

[ROAD_DETECTION]
model_path = models/road_detection_model/road_detection_best.pt
confidence_threshold = 0.5

[GARBAGE_DETECTION]
model_path = models/garbage_classification_model/best.pt
confidence_threshold = 0.75

[TEXT_ABUSE_DETECTION]
model_path = models/text_abuse_model/
confidence_threshold = 0.5
```

### **Environment Variables**
```bash
PORT=5001
DEBUG=False
MODEL_PATH=./models
CONFIDENCE_THRESHOLD=0.5
```

---

## 📊 Performance Metrics

### **Overall System Performance**
- **Average Accuracy**: 88.58%
- **Processing Time**: ~2.3 seconds per submission
- **System Uptime**: 99.7%
- **Memory Usage**: ~2GB RAM
- **CPU Usage**: ~45% during peak load

### **Model-Specific Metrics**
| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Road Detection | 94.2% | 93.5% | 94.9% | 94.2% |
| Garbage Detection | 92.8% | 91.5% | 94.1% | 92.8% |
| Privacy Protection | 90.6% | 85.2% | 96.3% | 90.6% |
| Abuse Detection | 76.8% | 78.5% | 75.1% | 76.8% |
| Text Abuse Detection | 89.5% | 92.1% | 87.2% | 89.5% |

---

## 📁 Project Structure

```
component_harish/
├── component_service.py          # Main Flask service (Port 5001)
├── working_demo.py             # Core validation logic
├── garbage_reporting_app.py     # Garbage-specific validation
├── distilbert_abuse_detector.py # Text analysis module
├── models/                     # Trained AI models
│   ├── abuse_detection_final/
│   │   ├── abuse_detection_best.pt
│   │   └── abuse_detection_last.pt
│   ├── human_detection_final/
│   │   ├── human_detection_best.pt
│   │   └── human_detection_last.pt
│   ├── garbage_classification_model/
│   │   ├── best.pt
│   │   ├── last.pt
│   │   └── results.csv
│   ├── trained_models_config.txt
│   └── road_parallel_results/    # Road model training results
├── data/                       # Dataset configurations
│   ├── road_damage_dataset.yaml
│   ├── road_relevancy_dataset.yaml
│   └── comprehensive_abusive_keywords.txt
├── training_curves_5_models/    # Training visualizations
│   ├── abuse_detection_training_curves.png
│   ├── garbage_classification_training_curves.png
│   ├── privacy_protection_training_curves.png
│   ├── road_detection_training_curves.png
│   └── text_abuse_detection_training_curves.png
├── abuse_detection_23456/      # Alternative model versions
├── enhanced_road_detection.py  # Enhanced road detection logic
├── emergency_road_detector.py  # Emergency road detection
└── README.md                   # This documentation
```

---

## 🔗 Repository Location

### **GitHub Repository**
- **Main Repository**: https://github.com/Vithushana/FinalYear-RP-VoiceUp
- **Main Branch**: `main`
- **Component Branch**: `harish`
- **Component Location**: `/component_harish/`
- **Issues**: https://github.com/Vithushana/FinalYear-RP-VoiceUp/issues

### **Local Folder Path**
- **Windows**: `c:\Users\Admin pc\Desktop\FinalYear-RP-VoiceUp\component_harish\`
- **README File**: `c:\Users\Admin pc\Desktop\FinalYear-RP-VoiceUp\component_harish\README.md`

### **Branch Information**
- **Main Branch**: Contains the complete VoiceUp platform with all components
- **Harish Branch**: Contains Harishram.M's Relevance and Abuse Filtration component updates
- **Switch to Harish Branch**: `git checkout harish`
- **View Branch**: `git branch -a`

---

## 🔗 Integration with VoiceUp

### **Upstream Services**
- **Main Backend** (Port 5000): Calls Relevance and Abuse Filtration for validation
- **Flutter App**: Submits content for validation via `/analyze` endpoint

### **Downstream Dependencies**
- **Main Backend Database**: Stores validated content
- **Notification System**: Sends strike warnings and confirmations

### **Communication Flow**
1. User submits content via Flutter app
2. Main backend forwards to Relevance and Abuse Filtration (Port 5001)
3. Component performs comprehensive validation using 5 AI models
4. Results returned with strike recommendations
5. Main backend processes results and notifies user

### **API Integration**
- **Endpoint**: `POST http://localhost:5001/analyze` 
- **Request**: Base64 image + description + issue_type
- **Response**: Validation results + strike recommendations
- **Processing Time**: ~2.3 seconds per submission

---

## 🎯 Key Achievements

### **Technical Excellence**
- **5 AI Models**: Comprehensive validation coverage
- **Real-time Processing**: Sub-2.3-second validation time
- **High Accuracy**: 88.58% average across all models
- **Privacy-First Design**: Advanced human detection capabilities

### **Innovation Highlights**
- **Progressive Strike System**: Smart violation management
- **Dual Notification System**: Enhanced user communication
- **Sector-Specific Validation**: Separate models for road and garbage
- **Context-Aware Validation**: Understands issue-specific requirements

### **Production Ready**
- **Scalable Architecture**: Microservice design
- **Robust Error Handling**: Comprehensive error management
- **Monitoring Ready**: Detailed logging and metrics
- **Easy Deployment**: Single-command startup

---

## 📊 VoiceUp System Overview

### **Complete Platform Architecture**
```
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
│   └── AI Validation Component
│       └── Relevance and Abuse Filtration (Port 5001) - Harishram.M
└── Database & Storage
    ├── PostgreSQL Database
    └── Image Storage
```

### **Validation Pipeline**
1. **User Submission** → Flutter App
2. **Pre-validation** → Relevance and Abuse Filtration (Harish)
3. **Final Processing** → Main Backend
4. **Storage** → Database + Notifications

---

**Relevance and Abuse Filtration - Harishram.M (IT22132178)** is the cornerstone of VoiceUp's content moderation system, ensuring a safe, relevant, and high-quality user experience while protecting user privacy and maintaining community standards.
