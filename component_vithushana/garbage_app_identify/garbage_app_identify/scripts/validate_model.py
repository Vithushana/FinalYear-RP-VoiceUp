from ultralytics import YOLO
import sys, json, os
path = 'd:/garbage_app_identify/best_v11.pt'
out_path = 'd:/garbage_app_identify/scripts/validate_output.json'
res = {"ok": False}
try:
    m = YOLO(path)
    res = {"ok": True, "class_count": len(m.names), "names": m.names}
except Exception as e:
    res = {"ok": False, "error": str(e)}
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
print('Wrote validation result to', out_path)
