import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from auth import auth_bp

load_dotenv()
PORT = int(os.getenv("PORT", "5000"))


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True, "service": "voiceup-backend", "status": "healthy"})

    app.register_blueprint(auth_bp)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=PORT, debug=True)
