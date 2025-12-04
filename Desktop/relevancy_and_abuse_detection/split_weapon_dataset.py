"""
Split Weapon Detection Dataset into 4 Parts - SIMPLE VERSION
Extracts, splits by folders directly, and zips each part
"""

import os
import zipfile
import shutil
from pathlib import Path

def extract_dataset(zip_path, extract_dir):
    """Extract the weapon detection dataset"""
    print(f"📦 Extracting...")
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"✅ Extracted")
    return extract_dir

def get_all_files(dataset_root):
    """Get all image and label files"""
    print("🔍 Scanning files...")
    
    files = {'train': [], 'valid': [], 'test': []}
    
    for split in ['train', 'valid', 'test']:
        images_dir = dataset_root / split / 'images'
        labels_dir = dataset_root / split / 'labels'
        
        if images_dir.exists():
            for img in images_dir.glob('*.*'):
                if img.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    label = labels_dir / f"{img.stem}.txt"
                    files[split].append({
                        'image': img,
                        'label': label if label.exists() else None
                    })
    
    total = sum(len(files[s]) for s in files)
    print(f"📊 Found {total} images")
    return files

def split_files_into_parts(files, num_parts=4):
    """Split files into equal parts"""
    print(f"✂️ Splitting into {num_parts} parts...")
    
    parts = [{'train': [], 'valid': [], 'test': []} for _ in range(num_parts)]
    
    for split in ['train', 'valid', 'test']:
        file_list = files[split]
        part_size = len(file_list) // num_parts
        
        for i in range(num_parts):
            start = i * part_size
            end = start + part_size if i < num_parts - 1 else len(file_list)
            parts[i][split] = file_list[start:end]
    
    for i, part in enumerate(parts, 1):
        total = sum(len(part[s]) for s in part)
        print(f"  Part {i}: {total} images")
    
    return parts

def create_part(part_data, part_num, output_dir):
    """Create a dataset part"""
    print(f"\n📁 Creating Part {part_num}...")
    part_dir = output_dir / f"weapon_detection_part_{part_num}"
    
    stats = {}
    for split in ['train', 'valid', 'test']:
        img_dir = part_dir / split / 'images'
        lbl_dir = part_dir / split / 'labels'
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        
        count = 0
        for item in part_data[split]:
            # Copy image
            shutil.copy2(item['image'], img_dir / item['image'].name)
            # Copy label
            if item['label'] and item['label'].exists():
                shutil.copy2(item['label'], lbl_dir / item['label'].name)
            count += 1
        stats[split] = count
        print(f"  {split}: {count} files")
    
    # Create data.yaml
    yaml_content = f"""path: .
train: train/images
val: valid/images
test: test/images
nc: 2
names: ['weapon', 'knife']
"""
    with open(part_dir / 'data.yaml', 'w') as f:
        f.write(yaml_content)
    
    return part_dir

def zip_part(part_dir):
    """Zip a dataset part"""
    zip_path = part_dir.parent / f"{part_dir.name}.zip"
    print(f"📦 Zipping Part {part_dir.name.split('_')[-1]}...")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(part_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(part_dir.parent)
                zipf.write(file_path, arcname)
    
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✅ {zip_path.name} ({size_mb:.2f} MB)")
    return zip_path

def main():
    print("="*60)
    print("WEAPON DETECTION DATASET SPLITTER - 4 PARTS")
    print("="*60)
    
    base_dir = Path(r"C:\Users\Admin pc\Desktop\relevancy_and_abuse_detection")
    zip_file = base_dir / "Weapon Detection.v1i.yolov8.zip"
    extract_dir = base_dir / "temp_weapon_extract"
    output_dir = base_dir / "weapon_detection_split"
    
    # Clean and create output
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()
    
    # Extract
    extract_dataset(zip_file, extract_dir)
    
    # Find dataset root (might be nested)
    dataset_root = extract_dir
    subdirs = [d for d in extract_dir.iterdir() if d.is_dir()]
    if subdirs and subdirs[0].name not in ['train', 'valid', 'test']:
        dataset_root = subdirs[0]
    
    # Get all files
    all_files = get_all_files(dataset_root)
    
    # Split into 4 parts
    parts = split_files_into_parts(all_files, 4)
    
    # Create each part and zip
    print("\n" + "="*60)
    zip_files = []
    for i, part_data in enumerate(parts, 1):
        part_dir = create_part(part_data, i, output_dir)
        zip_path = zip_part(part_dir)
        zip_files.append(zip_path)
        # Clean up unzipped folder
        shutil.rmtree(part_dir)
    
    # Cleanup
    shutil.rmtree(extract_dir)
    
    # Summary
    print("\n" + "="*60)
    print("🎉 COMPLETE!")
    print("="*60)
    print(f"📦 Created 4 zip files in: weapon_detection_split/")
    for zf in zip_files:
        print(f"   ✅ {zf.name}")
    print("="*60)

if __name__ == "__main__":
    main()
