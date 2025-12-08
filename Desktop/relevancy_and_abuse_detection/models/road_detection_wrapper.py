# ROAD DETECTION INTEGRATION WRAPPER
# Generated from trained road detection model
# Model: road_detection_model.pt

import cv2
import numpy as np
from ultralytics import YOLO
import torch
import os

class RoadDetector:
    def __init__(self, model_path="models/road_detection_model.pt"):
        """Initialize road detection model"""
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained road detection model"""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                print(f"Road detection model loaded: {self.model_path}")
            else:
                print(f"Road model not found: {self.model_path}")
                self.model = None
        except Exception as e:
            print(f"Error loading road model: {e}")
            self.model = None
    
    def detect_roads(self, image, confidence=0.3):
        """
        Detect roads in image
        
        Args:
            image: Input image (numpy array or path)
            confidence: Detection confidence threshold (0.0-1.0)
            
        Returns:
            dict: Detection results with roads found
        """
        if self.model is None:
            return {"roads_detected": False, "error": "Model not loaded"}
        
        try:
            # Run detection
            results = self.model(image, conf=confidence, verbose=False)
            
            roads_found = []
            has_roads = False
            
            for result in results:
                if result.boxes is not None and len(result.boxes) > 0:
                    has_roads = True
                    for box in result.boxes:
                        roads_found.append({
                            'confidence': float(box.conf[0]),
                            'class': int(box.cls[0]),
                            'bbox': box.xyxy[0].tolist()
                        })
            
            return {
                "roads_detected": has_roads,
                "road_count": len(roads_found),
                "detections": roads_found,
                "confidence_threshold": confidence
            }
            
        except Exception as e:
            return {"roads_detected": False, "error": str(e)}
    
    def draw_detections(self, image, detections, color=(0, 255, 0)):
        """Draw road detection boxes on image"""
        if not detections["roads_detected"]:
            return image
            
        img_copy = image.copy()
        
        for detection in detections["detections"]:
            bbox = detection["bbox"]
            conf = detection["confidence"]
            
            # Draw bounding box
            cv2.rectangle(img_copy, 
                         (int(bbox[0]), int(bbox[1])), 
                         (int(bbox[2]), int(bbox[3])), 
                         color, 2)
            
            # Add label
            label = f"Road: {conf:.2f}"
            cv2.putText(img_copy, label, 
                       (int(bbox[0]), int(bbox[1]-10)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return img_copy

# Usage example for integration:
# road_detector = RoadDetector()
# results = road_detector.detect_roads("test_image.jpg")
# print(f"Roads detected: {results['roads_detected']}")
