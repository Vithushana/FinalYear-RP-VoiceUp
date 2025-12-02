from flask import Blueprint, request, jsonify
from bson import ObjectId
from db import users
from utils import hash_password, verify_password, make_jwt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


@auth_bp.post("/signup")
def signup():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = _normalize_email(data.get("email"))
    password = data.get("password") or ""
    phone = (data.get("phone") or "").strip()
    position = (data.get("position") or "").strip()
    security_code = (data.get("securityCode") or "").strip()

    if not name or not email or not password:
        return jsonify({"ok": False, "message": "Name, email, and password are required."}), 400
    if "@" not in email:
        return jsonify({"ok": False, "message": "Invalid email."}), 400
    if len(password) < 6:
        return jsonify({"ok": False, "message": "Password must be at least 6 characters."}), 400

    try:
        users.insert_one({
            "name": name,
            "email": email,
            "password": hash_password(password),
            "phone": phone,
            "position": position,
            "securityCode": security_code,
        })
        return jsonify({"ok": True, "message": "Signup successful. Please log in."}), 201
    except Exception as e:
        msg = "Email already exists" if "duplicate key" in str(e).lower() else "Signup failed"
        return jsonify({"ok": False, "message": msg}), 409


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = _normalize_email(data.get("email"))
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"ok": False, "message": "Email and password are required."}), 400

    user = users.find_one({"email": email})
    if not user or not verify_password(password, user.get("password", b"")):
        return jsonify({"ok": False, "message": "Invalid credentials."}), 401

    token = make_jwt({"sub": str(user["_id"]), "email": email, "name": user.get("name", "")})
    return jsonify({"ok": True, "token": token, "user": {"id": str(user["_id"]), "name": user.get("name"), "email": email}}), 200
