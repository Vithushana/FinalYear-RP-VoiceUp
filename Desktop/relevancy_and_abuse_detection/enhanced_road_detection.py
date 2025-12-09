"""
Enhanced Road Detection System
Loads and uses all 8 trained road models for ensemble detection
"""
from ultralytics import YOLO
import os

class EnhancedRoadDetectionSystem:
    def __init__(self):
        """Load all 8 trained road models"""
        self.road_models = []
        
        # Load all 8 road models from road_parallel directory
        for i in range(1, 9):
            model_path = f"models/road_parallel/road_parallel_results/{i}/best.pt"
            if os.path.exists(model_path):
                try:
                    model = YOLO(model_path)
                    self.road_models.append(model)
                    print(f"✅ Enhanced detector loaded road model {i}/8")
                except Exception as e:
                    print(f"⚠️ Failed to load road model {i}: {e}")
        
        print(f"🎯 Enhanced Road Detector: {len(self.road_models)}/8 models loaded")
        
    def detect_roads_enhanced(self, image, confidence_threshold=0.15):
        """
        Run ensemble road detection using all loaded models
        Returns combined results from all models
        """
        all_detections = []
        
        # Run all models
        for model in self.road_models:
            try:
                results = model(image, verbose=False, conf=confidence_threshold)
                if results and len(results) > 0:
                    for result in results:
                        if hasattr(result, 'boxes') and result.boxes is not None:
                            for conf, cls_id in zip(result.boxes.conf.cpu().numpy(), result.boxes.cls.cpu().numpy()):
                                all_detections.append({
                                    'confidence': float(conf),
                                    'class': int(cls_id)
                                })
            except Exception as e:
                pass  # Skip failed models
        
        # Return results in expected format
        roads_detected = len(all_detections) > 0
        
        return {
            'roads_detected': roads_detected,
            'detections': all_detections,
            'num_models': len(self.road_models)
        }
