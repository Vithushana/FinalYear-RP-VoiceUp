from flask import Blueprint, jsonify
from app_sa.services_sa.fastapi_client_sa import forward_officer_complaint

officer_bp = Blueprint("officer_bp", __name__)

@officer_bp.get("/complaint/<int:complaint_id>")
def get_officer_complaint(complaint_id):
    try:
        out = forward_officer_complaint(complaint_id)
        return jsonify(out), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500