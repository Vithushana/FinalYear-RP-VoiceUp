from flask import Blueprint, request, jsonify
from models import db, User
from utils import hash_password, verify_password, generate_token, format_error_response, format_success_response

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Extract data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        mobile = data.get('mobile')
        position = data.get('position')
        province = data.get('province')
        district = data.get('district')
        
        # Validate required fields
        if not username or not email or not password:
            return format_error_response('Username, email, and password are required')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return format_error_response('Email already registered', 409)
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            mobile=mobile,
            position=position,
            province=province,
            district=district
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token
        token = generate_token(new_user.id)
        
        return format_success_response({
            'user': new_user.to_dict(),
            'token': token
        }, 'User registered successfully')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Registration failed: {str(e)}', 500)


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Accept either email or username for compatibility
        email = data.get('email') or data.get('username')
        password = data.get('password')
        
        # Validate required fields
        if not email or not password:
            return format_error_response('Email and password are required')
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not verify_password(user.password_hash, password):
            return format_error_response('Invalid email or password', 401)
        
        # Generate token
        token = generate_token(user.id)
        
        return format_success_response({
            'user': user.to_dict(),
            'token': token
        }, 'Login successful')
    
    except Exception as e:
        return format_error_response(f'Login failed: {str(e)}', 500)


@auth_bp.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    """Signup endpoint (alias for register) for website compatibility"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    
    try:
        data = request.get_json()
        
        # Map website fields to backend fields
        user_data = {
            'username': data.get('name', data.get('username')),
            'email': data.get('email'),
            'password': data.get('password'),
            'mobile': data.get('phone', data.get('mobile', ''))
        }
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not user_data.get(field):
                error_msg = f'Missing required field: {field}'
                return format_error_response(error_msg)
        
        # Check if email already exists (usernames can be duplicate)
        existing_email = User.query.filter_by(email=user_data['email']).first()
        if existing_email:
            error_msg = 'Email already exists'
            return format_error_response(error_msg)
        
        # Create new user
        new_user = User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=hash_password(user_data['password']),
            mobile=user_data['mobile']
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate token
        token = generate_token(new_user.id)
        
        return format_success_response({
            'user': new_user.to_dict(),
            'token': token
        }, 'User registered successfully')
    
    except Exception as e:
        db.session.rollback()
        
        # Convert SQL errors to user-friendly messages
        error_str = str(e).lower()
        if 'unique constraint' in error_str or 'integrity' in error_str:
            if 'email' in error_str:
                return format_error_response('Email already exists', 400)
            elif 'username' in error_str:
                return format_error_response('Username already exists', 400)
            else:
                return format_error_response('This information is already registered', 400)
        
        # Generic error for other cases
        return format_error_response('Registration failed. Please try again.', 500)


@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get user profile (requires authentication)"""
    try:
        # Get token from header
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return format_error_response('Invalid token format', 401)
        
        if not token:
            return format_error_response('Token is missing', 401)
        
        # Decode token
        from utils import decode_token
        payload = decode_token(token)
        if not payload:
            return format_error_response('Token is invalid or expired', 401)
        
        # Get user
        user = User.query.get(payload['user_id'])
        if not user:
            return format_error_response('User not found', 404)
        
        return format_success_response(user.to_dict())
    
    except Exception as e:
        return format_error_response(f'Failed to get profile: {str(e)}', 500)


@auth_bp.route('/anonymous-profile', methods=['POST'])
def save_anonymous_profile():
    """Save user's anonymous profile (display name and avatar)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        display_name = data.get('display_name')
        avatar_type = data.get('avatar_type')
        
        if not user_id or not display_name or not avatar_type:
            return format_error_response('user_id, display_name, and avatar_type are required', 400)
        
        # Find user
        user = User.query.get(user_id)
        if not user:
            return format_error_response('User not found', 404)
        
        # Update anonymous profile
        user.display_name = display_name
        user.avatar_type = avatar_type
        db.session.commit()
        
        return format_success_response({
            'user': user.to_dict()
        }, 'Anonymous profile saved successfully')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to save anonymous profile: {str(e)}', 500)