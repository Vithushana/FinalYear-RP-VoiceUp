import cv2
import numpy as np

class EmergencyRoadDetector:
    def __init__(self):
        pass
        
    def detect_road_emergency(self, image):
        # Basic heuristic implementation
        # Returns a dict as expected by working_demo.py
        
        if image is None:
            return {"is_road": False, "confidence": 0, "method": "Error", "indicators": []}
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        # Check for road-like colors (gray)
        avg_brightness = np.mean(gray)
        
        # Check for texture (roads are relatively smooth compared to forests, but textured compared to sky)
        variance = np.var(gray)
        
        is_road = False
        confidence = 0
        indicators = []
        
        if 40 < avg_brightness < 180:
            indicators.append("Brightness match")
            confidence += 30
            
        if 100 < variance < 3000:
            indicators.append("Texture match")
            confidence += 30
            
        # Check for lines (edges)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
        if lines is not None and len(lines) > 0:
            indicators.append("Lines detected")
            confidence += 30
            
        if confidence > 50:
            is_road = True
            
        return {
            "is_road": is_road,
            "confidence": confidence,
            "method": "Heuristic",
            "indicators": indicators
        }
