import os
from datetime import timedelta

class Config:
    """Flask application configuration"""
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "database.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Secret Key (change in production!)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    
    # File Upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # CORS
    CORS_ORIGINS = ['*']  # In production, specify Flutter app domain
    
    # Component Integration
    COMPONENT_TIMEOUT = 60  # seconds
    REQUIRE_ALL_COMPONENTS_PASS = True
    
    # Pagination
    POSTS_PER_PAGE = 20
    
    @staticmethod
    def init_app(app):
        """Initialize application"""
        # Create upload folder if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
