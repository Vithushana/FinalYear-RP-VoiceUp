"""
Unified Component 2 Service - Launcher
======================================
This script launches the unified Component 2 service which handles:
1. AI vs Real Detection (Port 5002 /analyze)
2. Garbage Classification (Port 5002 /classify)

Run this script to enable both features for the application.
"""

import os
import sys

# Path to the actual service script I created
SERVICE_SCRIPT = os.path.join(
    os.path.dirname(__file__), 
    "Garbage_Classification-main", 
    "Garbage_Classification-main", 
    "component_service.py"
)

if __name__ == "__main__":
    if not os.path.exists(SERVICE_SCRIPT):
        print(f"❌ Error: Service script not found at {SERVICE_SCRIPT}")
        sys.exit(1)
        
    print("\n" + "="*60)
    print("🚀 LAUNCHING COMPONENT 2 - UNIFIED SERVICE")
    print("="*60)
    print("Features: AI Detection + Garbage Classification")
    print("Port: 5002")
    print("="*60 + "\n")
    
    # Run the service script
    os.system(f"python \"{SERVICE_SCRIPT}\"")
