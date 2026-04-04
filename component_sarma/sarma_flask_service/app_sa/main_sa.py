from flask import Flask
from flask_cors import CORS

from app_sa.routes_sa.complaints_sa import complaints_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # allow Flutter Web / browser requests

    app.register_blueprint(complaints_bp, url_prefix="/api/complaints")

    @app.get("/")
    def home():
        return {"status": "Flask service running"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5004, debug=True)
