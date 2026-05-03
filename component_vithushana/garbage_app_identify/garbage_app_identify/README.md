# Garbage Identify & Classification 🚮

A YOLOv8-based Garbage Identification and Classification system that detects and classifies roadside garbage into multiple categories using Deep Learning.  
The project also includes a Flask-based web application for real-time image upload and the prediction.

---

## 📌 Project Overview

This project is designed to:
- Detect garbage objects from road images
- Classify them into predefined categories
- Provide real-time results via a web interface

The system is suitable for **smart city**, **road monitoring**, and **waste management** applications.

---

## 🧠 Model Details

- **Algorithm**: YOLOv8 (Object Detection)
- **Framework**: Ultralytics YOLO
- **Training Platform**: Google Colab (NVIDIA T4 GPU)
- **Backend**: Python Flask
- **Frontend**: HTML + JavaScript

---

## 🗂️ Garbage Categories

The model classifies garbage into **6 categories**:
1. BIODEGRADABLE  
2. CARDBOARD  
3. GLASS  
4. METAL  
5. PAPER  
6. PLASTIC  

---

## 📊 Model Performance (Final)

- **Precision**: ~61%
- **Recall**: ~48%
- **mAP@50**: ~55%
- **Inference Speed**: Real-time capable

> Dataset imbalance exists (e.g., fewer PAPER samples), which affects recall.

---

## 📁 Project Structure

```
garbage_app_identify/
├── app.py                 # Flask web application (main entry point)
├── best.pt               # YOLOv8 trained model (default)
├── best_v11.pt          # YOLOv11 trained model (alternate)
├── yolov11.pt           # Additional YOLOv11 weights
├── README.md            # Project documentation
├── data/
│   ├── images/
│   │   ├── train/       # Training images (6 garbage categories)
│   │   └── val/         # Validation images
│   └── labels/          # Annotation files (bounding boxes)
├── scripts/
│   ├── run_sample_predict.py  # Sample prediction script
│   ├── validate_model.py      # Model validation script
│   └── validate_output.json   # Validation metrics
├── static/
│   ├── uploads/         # Uploaded user images
│   └── results/         # Predicted output images (annotated)
├── templates/
│   └── index.html       # Web UI (upload & results display)
└── runs/
    └── detect/          # YOLOv8 training/validation outputs
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- GPU (optional, but recommended for faster inference)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/garbage_app_identify.git
   cd garbage_app_identify
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install flask ultralytics opencv-python
   ```

5. **Download model weights** (if not included)
   - Place `best.pt` (YOLOv8) or `best_v11.pt` (YOLOv11) in the project root

---

## 🎯 Usage

### Run the Flask Web Application

```bash
python app.py
```

The application will start on:
- Local: `http://127.0.0.1:5000`
- Network: `http://172.28.28.162:5000` (or your local IP)

### Features
1. **Upload Image**: Click to select or drag-drop a garbage image
2. **AI Detection**: Model identifies and classifies garbage types
3. **Environmental Advice**: Get tips for each garbage category
4. **View Results**: Annotated image with bounding boxes and confidence scores

### Model Selection
- **Default**: YOLOv8 model (`best.pt`)
- **Alternative**: YOLOv11 model (`best_v11.pt`)

---

## 🔍 API Endpoints

### `GET /`
Returns the home page (HTML interface)

### `POST /predict`
Predicts garbage classification from an uploaded image

**Request:**
```json
{
  "image": <image_file>,
  "model": "default" // or "yolov11"
}
```

**Response:**
```json
{
  "detections": [
    {
      "class_name": "PLASTIC",
      "confidence": 0.92,
      "bbox": [x1, y1, x2, y2],
      "advice": { ... }
    }
  ],
  "input_url": "/static/uploads/...",
  "result_url": "/static/results/.../..."
}
```

---

## ♻️ Environmental Advice System

Each garbage type includes tailored advice:

| Category | Severity | Action |
|----------|----------|--------|
| **PLASTIC** | 🔴 High | ❌ DO NOT LITTER - Recycle properly |
| **GLASS** | 🟡 Medium | ♻️ Recycle in glass bins |
| **METAL** | 🟡 Medium | ✅ Collect for recycling |
| **CARDBOARD** | 🟢 Low | 📦 Flatten & recycle |
| **PAPER** | 🟢 Low | 📰 Add to paper recycling |
| **BIODEGRADABLE** | 🟢 Low | 🌱 Compost or dispose naturally |

---

## 🧪 Testing & Validation

### Run Sample Predictions
```bash
python scripts/run_sample_predict.py
```

### Validate Model
```bash
python scripts/validate_model.py
```

Validation metrics are saved to `scripts/validate_output.json`

---

## 📈 Performance Metrics

- **Precision**: 61% - Accuracy of positive predictions
- **Recall**: 48% - Coverage of actual garbage objects
- **mAP@50**: 55% - Mean Average Precision at 50% IoU threshold
- **Inference Speed**: Real-time capable (suitable for edge devices)

> **Note**: Dataset imbalance affects recall. PAPER and GLASS categories have fewer samples.

---

## 🔧 Technologies Used

- **Deep Learning**: YOLOv8 / YOLOv11 (Ultralytics)
- **Backend**: Python Flask
- **Frontend**: HTML5 + JavaScript
- **Image Processing**: OpenCV (cv2)
- **Training**: Google Colab with NVIDIA T4 GPU

---

## 🌟 Key Features

✅ Real-time garbage detection & classification  
✅ Web-based user interface  
✅ Multiple model support (YOLOv8 & YOLOv11)  
✅ Environmental advice for each category  
✅ Image annotation with bounding boxes  
✅ High-confidence detection filtering  
✅ Automatic result caching & organization  

---

## 🚀 Future Enhancements

- [ ] Deploy on cloud (AWS/Azure/GCP)
- [ ] Mobile app integration
- [ ] Real-time video stream processing
- [ ] Improved dataset balance (collect more PAPER/GLASS samples)
- [ ] Model quantization for edge devices
- [ ] Database integration for result tracking
- [ ] Multi-language support

---

## 📝 License

This project is open-source and available under the MIT License.

---

## 👨‍💻 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📧 Contact & Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: your.email@example.com

---

**Happy Garbage Classification! 🚮🌍**
