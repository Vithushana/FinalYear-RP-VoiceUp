from ultralytics import YOLO
import os, cv2, json

# Paths
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WEIGHTS = os.path.join(ROOT, 'best_v11.pt')
OUT_DIR = os.path.join(ROOT, 'runs', 'sample_predict')
os.makedirs(OUT_DIR, exist_ok=True)

def find_sample_image():
    # look in val then train
    for split in ('val', 'train'):
        base = os.path.join(ROOT, 'data', 'images', split)
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    return os.path.join(root, f)
    return None

def main():
    if not os.path.exists(WEIGHTS):
        print('Weights not found:', WEIGHTS)
        return

    img = find_sample_image()
    if not img:
        print('No sample image found under data/images')
        return

    print('Using image:', img)
    model = YOLO(WEIGHTS)
    results = model.predict(source=img, conf=0.25, iou=0.5, save=False)
    r0 = results[0]

    detections = []
    for box in r0.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
        class_name = model.names.get(cls_id, str(cls_id))
        detections.append({
            'class_id': cls_id,
            'class_name': class_name,
            'confidence': conf,
            'bbox': [x1, y1, x2, y2]
        })

    out_img = r0.plot()
    out_path = os.path.join(OUT_DIR, 'sample_out.jpg')
    cv2.imwrite(out_path, cv2.cvtColor(out_img, cv2.COLOR_RGB2BGR))

    out_json = os.path.join(OUT_DIR, 'sample_out.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump({'image': img, 'detections': detections}, f, indent=2)

    print('Saved annotated image to', out_path)
    print('Saved detections to', out_json)

if __name__ == '__main__':
    main()
