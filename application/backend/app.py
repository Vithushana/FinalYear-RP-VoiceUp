from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from utils import init_database
from auth import auth_bp
from auth_otp import auth_bp as auth_otp_bp
from posts import posts_bp
from notifications import notifications_bp
from interactions import interactions_bp
from officer_routes import officer_bp
import os
from dotenv import load_dotenv

# Load environment variables from project root (new_version/.env)
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
load_dotenv(os.path.join(project_root, '.env'))

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(auth_otp_bp)  # OTP endpoints
    app.register_blueprint(posts_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(interactions_bp)
    app.register_blueprint(officer_bp)  # Officer/website routes
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
    
    # Root route
    @app.route('/')
    def index():
        return {
            'message': 'Voice Up Backend API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'posts': '/api/posts',
                'notifications': '/api/notifications'
            }
        }
    
    # Serve uploaded images
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        """Serve uploaded images"""
        from flask import send_from_directory
        import os
        uploads_dir = os.path.join(app.root_path, 'uploads')
        return send_from_directory(uploads_dir, filename)
    
    # Health check
    @app.route('/health')
    def health():
        return {'status': 'healthy'}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("🚀 Voice Up Backend Server Starting...")
    print("="*60)
    print("📍 Server: http://localhost:5000")
    print("📚 API Documentation:")
    print("   - Auth: http://localhost:5000/api/auth")
    print("   - Posts: http://localhost:5000/api/posts")
    print("   - Notifications: http://localhost:5000/api/notifications")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
