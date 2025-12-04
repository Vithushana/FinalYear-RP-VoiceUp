"""
WEAPON DETECTION TRAINING - GOOGLE COLAB
Train YOLOv8 model on weapon detection dataset (4 parts for parallel training)
"""

# ============================================================================
# CELL 1: Setup and Installation
# ============================================================================
print("🚀 Installing required packages...")
!pip install ultralytics -q
!pip install roboflow -q

from ultralytics import YOLO
import os
from pathlib import Path
import shutil

print("✅ Installation complete!")

# ============================================================================
# CELL 2: Setup Working Directory
# ============================================================================
print("📁 Setting up working directory...")

# Create working directory
WORK_DIR = Path('/content/weapon_detection')
WORK_DIR.mkdir(exist_ok=True)
os.chdir(WORK_DIR)

print(f"✅ Working directory: {WORK_DIR}")

# ============================================================================
# CELL 3: Upload Dataset Part
# ============================================================================
print("📦 Upload your weapon detection dataset part...")
print("Choose which part to train: part_1, part_2, part_3, or part_4")

from google.colab import files
uploaded = files.upload()

# Get the uploaded zip filename
zip_file = list(uploaded.keys())[0]
print(f"✅ Uploaded: {zip_file}")

# Extract dataset
import zipfile
print(f"📂 Extracting {zip_file}...")
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(WORK_DIR)

# Find the dataset directory
dataset_dirs = [d for d in WORK_DIR.iterdir() if d.is_dir() and 'weapon_detection_part' in d.name]
if dataset_dirs:
    DATASET_DIR = dataset_dirs[0]
    print(f"✅ Dataset extracted to: {DATASET_DIR}")
else:
    print("❌ Could not find dataset directory!")

# ============================================================================
# CELL 4: Verify Dataset Structure
# ============================================================================
print("\n🔍 Verifying dataset structure...")

# Check for data.yaml
data_yaml = DATASET_DIR / 'data.yaml'
if data_yaml.exists():
    print("✅ Found data.yaml")
    
    # Read and fix paths in data.yaml
    with open(data_yaml, 'r') as f:
        yaml_content = f.read()
    
    print("Original data.yaml:")
    print(yaml_content)
    
    # Fix paths to be absolute
    import re
    yaml_content = re.sub(r'path:.*', f'path: {DATASET_DIR}', yaml_content)
    yaml_content = re.sub(r'train:.*', 'train: train/images', yaml_content)
    yaml_content = re.sub(r'val:.*', 'val: valid/images', yaml_content)
    yaml_content = re.sub(r'test:.*', 'test: test/images', yaml_content)
    
    # Write corrected data.yaml
    with open(data_yaml, 'w') as f:
        f.write(yaml_content)
    
    print("\n✅ Fixed data.yaml:")
    print(yaml_content)
else:
    print("❌ data.yaml not found!")

# Count images
train_images = list((DATASET_DIR / 'train' / 'images').glob('*.jpg')) + \
               list((DATASET_DIR / 'train' / 'images').glob('*.png'))
valid_images = list((DATASET_DIR / 'valid' / 'images').glob('*.jpg')) + \
               list((DATASET_DIR / 'valid' / 'images').glob('*.png'))
test_images = list((DATASET_DIR / 'test' / 'images').glob('*.jpg')) + \
              list((DATASET_DIR / 'test' / 'images').glob('*.png'))

print(f"\n📊 Dataset Statistics:")
print(f"   Train: {len(train_images)} images")
print(f"   Valid: {len(valid_images)} images")
print(f"   Test: {len(test_images)} images")
print(f"   Total: {len(train_images) + len(valid_images) + len(test_images)} images")

# ============================================================================
# CELL 5: Initialize YOLOv8 Model
# ============================================================================
print("\n🤖 Initializing YOLOv8 model...")

# Choose model size (n=nano, s=small, m=medium, l=large, x=xlarge)
MODEL_SIZE = 'm'  # Medium model - good balance
print(f"📦 Using YOLOv8{MODEL_SIZE}")

model = YOLO(f'yolov8{MODEL_SIZE}.pt')
print("✅ Model initialized!")

# ============================================================================
# CELL 6: Configure Training Parameters
# ============================================================================
print("\n⚙️ Configuring training parameters...")

TRAINING_CONFIG = {
    'data': str(data_yaml),
    'epochs': 100,              # Number of training epochs
    'imgsz': 640,              # Image size
    'batch': 16,               # Batch size (adjust based on GPU)
    'patience': 20,            # Early stopping patience
    'save': True,              # Save checkpoints
    'device': 0,               # GPU device (0 for first GPU)
    'workers': 8,              # Number of workers
    'project': 'weapon_detection_results',
    'name': f'weapon_part_{DATASET_DIR.name.split("_")[-1]}',
    'exist_ok': True,
    'pretrained': True,
    'optimizer': 'auto',
    'verbose': True,
    'seed': 42,
    'deterministic': False,
    'single_cls': False,
    'rect': False,
    'cos_lr': True,            # Cosine learning rate scheduler
    'close_mosaic': 10,        # Disable mosaic augmentation in last N epochs
    'resume': False,
    'amp': True,               # Automatic Mixed Precision
    'fraction': 1.0,
    'profile': False,
    'freeze': None,
    'lr0': 0.01,               # Initial learning rate
    'lrf': 0.01,               # Final learning rate
    'momentum': 0.937,
    'weight_decay': 0.0005,
    'warmup_epochs': 3.0,
    'warmup_momentum': 0.8,
    'warmup_bias_lr': 0.1,
    'box': 7.5,                # Box loss weight
    'cls': 0.5,                # Class loss weight
    'dfl': 1.5,                # Distribution focal loss weight
    'pose': 12.0,
    'kobj': 1.0,
    'label_smoothing': 0.0,
    'nbs': 64,
    'overlap_mask': True,
    'mask_ratio': 4,
    'dropout': 0.0,
    'val': True,
}

print("✅ Training configuration ready!")
print("\n📋 Key Parameters:")
print(f"   Epochs: {TRAINING_CONFIG['epochs']}")
print(f"   Batch Size: {TRAINING_CONFIG['batch']}")
print(f"   Image Size: {TRAINING_CONFIG['imgsz']}")
print(f"   Model: YOLOv8{MODEL_SIZE}")

# ============================================================================
# CELL 7: Start Training
# ============================================================================
print("\n" + "="*60)
print("🚀 STARTING WEAPON DETECTION TRAINING")
print("="*60)
print("⏰ This will take 1-2 hours depending on dataset size...")
print("📊 Training progress will be displayed below")
print("="*60 + "\n")

# Train the model
results = model.train(**TRAINING_CONFIG)

print("\n" + "="*60)
print("✅ TRAINING COMPLETED!")
print("="*60)

# ============================================================================
# CELL 8: Evaluate Model
# ============================================================================
print("\n📊 Evaluating trained model...")

# Evaluate on validation set
metrics = model.val()

print("\n🎯 Model Performance Metrics:")
print(f"   mAP50: {metrics.box.map50:.4f}")
print(f"   mAP50-95: {metrics.box.map:.4f}")
print(f"   Precision: {metrics.box.mp:.4f}")
print(f"   Recall: {metrics.box.mr:.4f}")

# ============================================================================
# CELL 9: Test on Sample Images
# ============================================================================
print("\n🔍 Testing model on sample images...")

# Get some test images
test_img_dir = DATASET_DIR / 'test' / 'images'
test_images = list(test_img_dir.glob('*.jpg'))[:5]  # First 5 test images

if test_images:
    print(f"Testing on {len(test_images)} sample images...")
    
    for img_path in test_images:
        results = model.predict(
            source=str(img_path),
            conf=0.25,
            save=True,
            project='weapon_detection_results',
            name='predictions'
        )
        print(f"✅ Processed: {img_path.name}")
    
    print("\n✅ Sample predictions saved!")
else:
    print("⚠️ No test images found")

# ============================================================================
# CELL 10: Download Trained Models
# ============================================================================
print("\n📥 Downloading trained models...")

from google.colab import files

# Find the trained models
results_dir = Path('weapon_detection_results')
part_name = DATASET_DIR.name.split('_')[-1]
model_dir = results_dir / f'weapon_part_{part_name}' / 'weights'

if model_dir.exists():
    best_model = model_dir / 'best.pt'
    last_model = model_dir / 'last.pt'
    
    # Download best model
    if best_model.exists():
        print(f"📦 Downloading best.pt...")
        files.download(str(best_model))
        print("✅ Downloaded: best.pt")
    else:
        print("⚠️ best.pt not found")
    
    # Download last model
    if last_model.exists():
        print(f"📦 Downloading last.pt...")
        files.download(str(last_model))
        print("✅ Downloaded: last.pt")
    else:
        print("⚠️ last.pt not found")
    
    # Download training results CSV
    results_csv = results_dir / f'weapon_part_{part_name}' / 'results.csv'
    if results_csv.exists():
        print(f"📦 Downloading results.csv...")
        files.download(str(results_csv))
        print("✅ Downloaded: results.csv")
    else:
        print("⚠️ results.csv not found")
    
    # Download confusion matrix
    confusion_matrix = results_dir / f'weapon_part_{part_name}' / 'confusion_matrix.png'
    if confusion_matrix.exists():
        print(f"📦 Downloading confusion_matrix.png...")
        files.download(str(confusion_matrix))
        print("✅ Downloaded: confusion_matrix.png")
    
    print("\n✅ All files downloaded to your computer!")
else:
    print("❌ Could not find trained models!")

print("\n🎉 TRAINING COMPLETE!")
print("="*60)
print("📦 Downloaded files:")
print("   - best.pt (best performing model)")
print("   - last.pt (last epoch model)")
print("   - results.csv (training metrics)")
print("   - confusion_matrix.png (if available)")
print("="*60)
