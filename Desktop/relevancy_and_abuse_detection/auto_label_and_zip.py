"""
Automatic Label Generator for Road Parallel Datasets
Creates YOLO format labels for all images in the 8 parallel dataset folders
"""

import os
import zipfile
import shutil
from pathlib import Path
from PIL import Image
import cv2

def create_yolo_label(image_path, class_id=0):
    """
    Create a YOLO format label for a full-image classification
    Args:
        image_path: Path to the image file
        class_id: Class ID (0 = road by default)
    Returns:
        YOLO format label string: "class_id x_center y_center width height"
    """
    # For full-image classification: center at 0.5, 0.5, size 1.0 x 1.0
    return f"{class_id} 0.5 0.5 1.0 1.0"

def process_dataset_part(zip_path, output_dir):
    """
    Extract zip, generate labels for all images, and re-zip
    """
    print(f"\n{'='*60}")
    print(f"Processing: {zip_path.name}")
    print(f"{'='*60}")
    
    # Create temporary extraction directory
    extract_dir = output_dir / f"temp_{zip_path.stem}"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True)
    
    # Extract the zip file
    print(f"📦 Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    # Find the actual dataset folder (might be nested)
    dataset_folders = [f for f in extract_dir.iterdir() if f.is_dir()]
    if len(dataset_folders) == 1:
        dataset_root = dataset_folders[0]
    else:
        dataset_root = extract_dir
    
    print(f"📁 Dataset root: {dataset_root}")
    
    # Process train, valid, test splits
    splits = ['train', 'valid', 'test']
    total_images = 0
    total_labels_created = 0
    
    for split in splits:
        images_dir = dataset_root / split / 'images'
        labels_dir = dataset_root / split / 'labels'
        
        if not images_dir.exists():
            print(f"⚠️  {split}/images not found, skipping...")
            continue
        
        # Create labels directory if it doesn't exist
        labels_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        image_files = []
        for ext in image_extensions:
            image_files.extend(list(images_dir.glob(f"*{ext}")))
            image_files.extend(list(images_dir.glob(f"*{ext.upper()}")))
        
        print(f"\n📸 Processing {split}: {len(image_files)} images")
        
        # Generate labels for each image
        for img_path in image_files:
            # Create label file path
            label_path = labels_dir / f"{img_path.stem}.txt"
            
            # Generate YOLO format label (full image = road)
            label_content = create_yolo_label(img_path, class_id=0)
            
            # Write label file
            with open(label_path, 'w') as f:
                f.write(label_content + '\n')
            
            total_labels_created += 1
        
        total_images += len(image_files)
        print(f"   ✅ Created {len(image_files)} label files in {split}/labels/")
    
    # Create data.yaml if it doesn't exist
    yaml_path = dataset_root / 'data.yaml'
    if not yaml_path.exists():
        yaml_content = f"""# Road Detection Dataset - {zip_path.stem}
# Auto-generated labels for parallel training

path: {dataset_root.absolute()}
train: train/images
val: valid/images
test: test/images

# Classes
nc: 1
names: ['road']

# Dataset Info
total_images: {total_images}
auto_labeled: true
label_format: YOLO (full image classification)
"""
        with open(yaml_path, 'w') as f:
            f.write(yaml_content)
        print(f"\n📄 Created data.yaml")
    
    # Re-zip the dataset
    new_zip_path = output_dir / zip_path.name
    print(f"\n📦 Creating new zip file: {new_zip_path.name}")
    
    with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dataset_root):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(dataset_root.parent)
                zipf.write(file_path, arcname)
    
    # Clean up temporary extraction
    shutil.rmtree(extract_dir)
    
    print(f"✅ Completed: {total_images} images, {total_labels_created} labels created")
    print(f"💾 Saved as: {new_zip_path}")
    
    return total_images, total_labels_created

def main():
    """Main function to process all 8 dataset parts"""
    print("="*60)
    print("AUTOMATIC LABEL GENERATOR FOR ROAD PARALLEL DATASETS")
    print("="*60)
    print("🎯 Purpose: Generate YOLO labels for all road images")
    print("📊 Format: Full-image classification (class 0 = road)")
    print("="*60)
    
    # Setup paths
    base_dir = Path(r"C:\Users\Admin pc\Desktop\relevancy_and_abuse_detection")
    datasets_dir = base_dir / "road_parallel_datasets"
    output_dir = base_dir / "road_parallel_datasets_labeled"
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Process all 8 parts
    zip_files = sorted(datasets_dir.glob("road_dataset_part_*.zip"))
    
    if not zip_files:
        print("❌ No dataset zip files found!")
        return
    
    print(f"\n📦 Found {len(zip_files)} dataset parts to process\n")
    
    grand_total_images = 0
    grand_total_labels = 0
    
    for zip_path in zip_files:
        try:
            images, labels = process_dataset_part(zip_path, output_dir)
            grand_total_images += images
            grand_total_labels += labels
        except Exception as e:
            print(f"❌ Error processing {zip_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*60)
    print("🎉 LABELING COMPLETE!")
    print("="*60)
    print(f"📊 Total Images Processed: {grand_total_images:,}")
    print(f"🏷️  Total Labels Created: {grand_total_labels:,}")
    print(f"💾 Output Directory: {output_dir}")
    print("="*60)
    print("\n✅ All datasets have been labeled and re-zipped!")
    print("📁 Find your labeled datasets in: road_parallel_datasets_labeled/")
    print("\n🚀 Ready for parallel training on Google Colab!")

if __name__ == "__main__":
    main()
