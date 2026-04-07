from flask import Blueprint, request, jsonify
from app_sa.services_sa.fastapi_client_sa import forward_submit_complaint, forward_list_all, forward_expand_text
complaints_bp = Blueprint("complaints_bp", __name__)

@complaints_bp.post("/submit")
def submit():
    data = request.get_json(silent=True) or {}

    # Flutter fields -> convert to FastAPI fields
    issue_type = (data.get("issueType") or "").lower().strip()   # Road/Garbage
    category = "road" if issue_type == "road" else "garbage"

    # coomplaints_sa.py kulla
    payload = {
        "category": data.get("category") or category,
        "text": data.get("text", ""),
        "expand_text": data.get("expand_text", True),
        "location_link": data.get("location_link"),
        "latitude": data.get("latitude"),
        "longitude": data.get("longitude"),
    }

    # Basic validation (so FastAPI gets clean)
    if not payload["text"]:
        return jsonify({"error": "description is required"}), 400

    try:
        out = forward_submit_complaint(payload)
        return jsonify(out), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@complaints_bp.get("/all")
def all_complaints():
    try:
        out = forward_list_all()
        return jsonify(out), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@complaints_bp.route("/expand", methods=["POST", "OPTIONS"]) # OPTIONS for CORS preflight
def expand():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
        
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "Text is required for expansion"}), 400
        
    try:
        # FastAPI backend engine (Port 8000)-kku request-ah forward pannum
        out = forward_expand_text({"text": text}) 
        return jsonify(out), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500