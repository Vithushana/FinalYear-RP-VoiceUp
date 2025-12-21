import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import os
import base64
from PIL import Image
import io

def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')
    return token

def decode_token(token):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        # Add user_id to kwargs
        kwargs['current_user_id'] = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated

def hash_password(password):
    """Hash password using werkzeug"""
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """Verify password against hash"""
    return check_password_hash(password_hash, password)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_image(image_data, filename):
    """
    Save image to uploads folder
    Accepts base64 encoded image (with or without data URI prefix) or file upload
    Returns: filepath relative to uploads folder
    """
    try:
        print(f"      🔍 save_image called with filename: {filename}")
        print(f"      🔍 image_data type: {type(image_data)}")
        
        # Create uploads folder if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        
        # Handle string data (base64)
        if isinstance(image_data, str):
            print(f"      🔍 Processing base64 string (length: {len(image_data)})")
            
            # Check if it has data URI prefix
            if image_data.startswith('data:image'):
                print(f"      ✅ Has data:image prefix, extracting base64...")
                # Extract base64 data after comma
                image_data = image_data.split(',')[1]
            else:
                print(f"      ✅ Raw base64 string (no prefix)")
            
            # Decode base64
            try:
                image_bytes = base64.b64decode(image_data)
                print(f"      ✅ Decoded {len(image_bytes)} bytes")
            except Exception as decode_error:
                print(f"      ❌ Base64 decode error: {decode_error}")
                return None
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            print(f"      ✅ Image saved to: {filepath}")
            
        else:
            # Assume it's a file object
            print(f"      🔍 Processing as file object")
            image_data.save(filepath)
            print(f"      ✅ Image saved as file object to: {filepath}")
        
        # Return relative path
        print(f"      ✅ Returning filename: {unique_filename}")
        return unique_filename
    
    except Exception as e:
        print(f"      ❌ Error saving image: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_image_base64(filename):
    """Get image as base64 encoded string"""
    try:
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        with open(filepath, 'rb') as f:
            image_data = f.read()
        
        # Encode to base64
        base64_data = base64.b64encode(image_data).decode('utf-8')
        
        # Determine image type
        ext = filename.rsplit('.', 1)[1].lower()
        mime_type = f'image/{ext}'
        
        return f'data:{mime_type};base64,{base64_data}'
    
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

def format_error_response(message, status_code=400):
    """Format error response"""
    return jsonify({
        'success': False,
        'error': message
    }), status_code

def format_success_response(data, message=None):
    """Format success response"""
    response = {
        'success': True,
        'data': data
    }
    if message:
        response['message'] = message
    return jsonify(response), 200

def init_database(app, db):
    """Initialize database with tables"""
    with app.app_context():
        db.create_all()
        print("✅ Database initialized successfully")
