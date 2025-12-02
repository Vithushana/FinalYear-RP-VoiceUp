from road_detection_integration import RoadDetectionSystem

class EnhancedRoadDetectionSystem:
    def __init__(self):
        self.detector = RoadDetectionSystem()
        
    def detect_roads_enhanced(self, image, confidence_threshold=0.15):
        # Map the method call to the existing one
        return self.detector.detect_roads_in_image(image, confidence_threshold)
