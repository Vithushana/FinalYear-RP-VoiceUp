from ultralytics import YOLO

if __name__ == "__main__":
    model = YOLO("yolov8m.pt")  

    model.train(
        data="config.yaml",
        epochs=50,
        batch=8,
        imgsz=960,
        device=0,
        workers=0, 
        cache=True,
        name="train2"
    )
