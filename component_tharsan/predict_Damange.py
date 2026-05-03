from ultralytics import YOLO
import cv2

# Paths
MODEL_PATH = "runs/detect/train2/weights/best.pt"
IMAGE_PATH = r"test\2.jpg"

# Load model
model = YOLO(MODEL_PATH)

# Predict
results = model.predict(
    source=IMAGE_PATH,
    imgsz=640,
    conf=0.5,
    save=False,
    show=False
)

# Check and print detections
if not results[0].boxes or len(results[0].boxes) == 0:
    print("No objects detected")
else:
    for box in results[0].boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        print(f"{model.names[cls]} | conf={conf:.3f} | box={xyxy}")

 
annotated_image = results[0].plot()   
annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)  

cv2.imshow("YOLO Detections", annotated_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
