# AI-Powered Road Damage Detection & Content Filtration System

## Project Overview
This is **Harish's AI Detection Backend** - a comprehensive road damage detection and content filtration system that operates independently from the VoiceUp website backend.

## Important Note
⚠️ **This AI Detection project is completely separate from the VoiceUp website backend.**
- Both are Python-based backends but have **NO connection** to each other
- This project focuses on AI-powered image analysis for road damage detection
- The VoiceUp website backend handles user authentication, posts, and social features
- They operate in **separate folders** and have different purposes

## Project Structure

```
relevancy_and_abuse_detection/          # AI Detection Backend (THIS PROJECT)
├── src/                                 # Core detection modules
│   ├── abuse_detector.py               # Abuse content detection
│   ├── relevancy_detector.py           # Road relevancy detection
│   └── __init__.py
├── models/                              # Trained AI models
│   ├── abuse_detection_final/          # Abuse detection models
│   ├── road_detection_ultimate/        # Road detection models
│   ├── human_detection_final/          # Privacy protection models
│   └── road_detection_model.pt
├── data/                                # Dataset configurations
│   ├── comprehensive_abusive_keywords.txt
│   ├── road_damage_dataset.yaml
│   └── road_relevancy_dataset.yaml
├── working_demo.py                      # Main Flask application
├── emergency_road_detector.py           # Emergency fallback detector
├── enhanced_road_detection.py           # Enhanced detection system
├── config.py                            # Configuration settings
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

## Features

### 1. Road Damage Detection
- **AI-Powered Detection**: Custom-trained YOLOv8 models for road damage classification
- **Multiple Model Ensemble**: Combines predictions from multiple trained models
- **Categories Detected**:
  - Potholes
  - Cracks (Alligator, Lateral, Longitudinal)
  - Road surface damage
  - Combination damage

### 2. Content Filtration System
- **Privacy Protection**: Automatic human detection and privacy filtering
- **Abuse Detection**: Multi-category abuse content detection
- **Relevancy Check**: Binary classification (road vs non-road images)

### 3. Two-Phase Filtration
**Phase 1**: Relevance Check
- Only road-related issues allowed
- AI-powered road detection with high confidence thresholds

**Phase 2**: Complete Abuse Check
- Image abuse detection (nudity, violence, hate symbols)
- Text context analysis
- Privacy protection (human detection)

## Technology Stack

### AI/ML Framework
- **YOLOv8**: Object detection for road damage and abuse content
- **TensorFlow/Keras**: Custom CNN models
- **OpenCV**: Image processing and traditional CV methods

### Backend Framework
- **Flask**: Web application framework
- **Python 3.8+**: Core programming language

### Key Libraries
- `ultralytics` - YOLOv8 implementation
- `tensorflow` - Deep learning framework
- `opencv-python` - Computer vision
- `numpy` - Numerical computing
- `Pillow` - Image processing

## Installation

### Prerequisites
```bash
Python 3.8 or higher
pip (Python package manager)
```

### Setup
```bash
# Clone the repository
git clone https://github.com/Vithushana/FinalYear-RP-VoiceUp.git
cd FinalYear-RP-VoiceUp
git checkout harish

# Navigate to AI Detection project
cd relevancy_and_abuse_detection

# Install dependencies
pip install -r requirements.txt
```

### Download Models
Models are stored separately due to size constraints:
1. Download trained models from Google Drive (link provided separately)
2. Extract to `models/` directory
3. Verify model paths in `config.py`

## Usage

### Running the Demo Application
```bash
python working_demo.py
```
Access at: `http://localhost:8080`

### API Endpoints

#### POST /analyze
Analyze uploaded image and description
```json
{
  "image": "base64_encoded_image_data",
  "description": "Image description text"
}
```

**Response:**
```json
{
  "privacy_protection": {...},
  "relevancy_check": {...},
  "abuse_detection": {...},
  "final_decision": {
    "status": "ACCEPTED/REJECTED",
    "accepted": true/false,
    "reason": "Detailed reason",
    "strike_issued": false,
    "system_type": "AI Detection System"
  }
}
```

## Model Information

### Road Detection Models
- **Primary**: `models/road_detection_ultimate/training/weights/best.pt`
- **Secondary**: `models/road_detection_model.pt`
- **Performance**: 
  - mAP50: ~85-90%
  - Confidence threshold: 70%+ for strict filtering

### Abuse Detection Model
- **Path**: `models/abuse_detection_final/abuse_detection_best.pt`
- **Performance**: 
  - mAP50: 96.5%
  - Trained for 69 epochs

### Human Detection Model
- **Path**: `models/human_detection_final/human_detection_best.pt`
- **Performance**: 
  - mAP50: 90.6%
  - Privacy protection feature

## Dataset Preparation

### Automatic Label Generation
Use the auto-labeling script for road datasets:
```bash
python auto_label_and_zip.py
```

This generates YOLO format labels for all images:
- Format: `0 0.5 0.5 1.0 1.0` (full-image classification)
- Class 0 = road
- Creates proper train/valid/test structure

## Configuration

Edit `config.py` to customize:
- Model paths
- Confidence thresholds
- Image preprocessing parameters
- Training hyperparameters

## Development

### Adding New Detection Categories
1. Prepare labeled dataset
2. Train YOLOv8 model
3. Update `config.py` with model path
4. Integrate into detection pipeline

### Testing
```bash
# Run system tests
python test_analysis_system.py
```

## Project Status
✅ **Production Ready**
- All models trained and integrated
- Privacy protection enabled
- Two-phase filtration active
- Demo application functional

## Important Notes

### Separation from Website Backend
- This AI Detection system is **independent** from the VoiceUp social platform
- No shared database or API endpoints
- Can be deployed separately
- Different deployment environments

### Model Storage
- Large model files (.pt, .h5) are not included in Git
- Download from provided Google Drive link
- Total size: ~500MB-1GB

### Dataset Storage
- Training datasets are excluded from Git
- Use provided dataset preparation scripts
- Store locally or on cloud storage

## Future Enhancements
- [ ] Real-time video analysis
- [ ] Multi-language text abuse detection
- [ ] Advanced damage severity assessment
- [ ] Geolocation-based damage tracking
- [ ] Integration with mobile applications

## Contributors
- **Harish** (harish012801@gmail.com) - AI Detection System Developer

## License
Part of VoiceUp Final Year Project

## Contact
For questions about the AI Detection system:
- Email: harish012801@gmail.com
- GitHub: [VoiceUp Repository - Harish Branch](https://github.com/Vithushana/FinalYear-RP-VoiceUp/tree/harish)

---

**Last Updated**: December 2, 2025
**Version**: 1.0.0
