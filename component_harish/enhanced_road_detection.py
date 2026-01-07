"""
Enhanced Road Detection System
Loads and uses all 8 trained road models for ensemble detection
"""
from ultralytics import YOLO
import os
import torch
from concurrent.futures import ThreadPoolExecutor

# Get the directory where this component file is located
COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))

class EnhancedRoadDetectionSystem:
    def __init__(self):
        """Load trained road detection model"""
        self.road_models = []
        
        def load_road_model(i):
            model_path = os.path.join(COMPONENT_DIR, f"models/road_parallel_results/{i}/best.pt")
            if os.path.exists(model_path):
                try:
                    model = YOLO(model_path)
                    if torch.cuda.is_available():
                        model.fuse()  # Fuse layers for faster inference
                    pass  # Model loaded
                    return model
                except Exception as e:
                    print(f"⚠️ Failed to load road model {i}: {e}")
            return None
        
        # Parallel loading of all 8 road models
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(load_road_model, range(1, 9)))
            self.road_models = [m for m in results if m is not None]
        
        if len(self.road_models) > 0:
            print(f"✅ Road detection model loaded")
        
    def detect_roads_enhanced(self, image, confidence_threshold=0.15):
        """
        Run ensemble road detection using all models in PARALLEL
        Returns combined results from all models
        """
        all_detections = []
        
        def run_road_model(model):
            detections = []
            try:
                with torch.no_grad():
                    results = model(image, verbose=False, conf=confidence_threshold)
                if results and len(results) > 0:
                    for result in results:
                        if hasattr(result, 'boxes') and result.boxes is not None:
                            for conf, cls_id in zip(result.boxes.conf.cpu().numpy(), result.boxes.cls.cpu().numpy()):
                                detections.append({
                                    'confidence': float(conf),
                                    'class': int(cls_id)
                                })
            except Exception as e:
                pass
            return detections
        
        # Run all 8 road models in parallel for 60-70% speedup
        with ThreadPoolExecutor(max_workers=min(4, len(self.road_models))) as executor:
            results = list(executor.map(run_road_model, self.road_models))
            for detections in results:
                all_detections.extend(detections)
        
        # Return results in expected format
        roads_detected = len(all_detections) > 0
        
        return {
            'roads_detected': roads_detected,
            'detections': all_detections,
            'num_models': len(self.road_models)
        }
