import os
import random
import shutil

IMAGE_DIR = "Data/images"
LABEL_DIR = "Data/labels"

TRAIN_RATIO = 0.8

# Output dirs
for p in [
    "Data/images/train", "Data/images/val",
    "Data/labels/train", "Data/labels/val"
]:
    os.makedirs(p, exist_ok=True)

images = [f for f in os.listdir(IMAGE_DIR) if f.endswith((".jpg", ".png"))]
random.shuffle(images)

split_idx = int(len(images) * TRAIN_RATIO)
train_imgs = images[:split_idx]
val_imgs = images[split_idx:]

def move(files, img_dst, lbl_dst):
    for f in files:
        shutil.copy(
            os.path.join(IMAGE_DIR, f),
            os.path.join(img_dst, f)
        )
        label = f.rsplit(".", 1)[0] + ".txt"
        shutil.copy(
            os.path.join(LABEL_DIR, label),
            os.path.join(lbl_dst, label)
        )

move(train_imgs, "Data/images/train", "Data/labels/train")
move(val_imgs, "Data/images/val", "Data/labels/val")

print("--> Dataset split completed")
print(f"Train: {len(train_imgs)} images")
print(f"Val: {len(val_imgs)} images")
