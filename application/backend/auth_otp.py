from flask import Blueprint, request, jsonify
from models import db, User
from utils import hash_password, verify_password, generate_token, format_error_response, format_success_response
from otp_service import send_otp_to_phone, verify_otp, otp_storage
import traceback

auth_bp = Blueprint('auth_otp', __name__, url_prefix='/api/auth')

# Temporary storage for pending signups (in production, use Redis or database)
pending_signups = {}

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP to phone number during signup"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return format_error_response('Phone number is required')
        
        # Format phone number to E.164 format for Twilio
        # Convert Sri Lankan numbers: 0770517706 -> +94770517706
        original_phone = phone
        if phone.startswith('0'):
            phone = '+94' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+94' + phone
        
        print(f"📱 Phone number formatting: {original_phone} -> {phone}")
        
        # Store signup data temporarily
        signup_data = {
            'name': data.get('name'),
            'email': data.get('email'),
            'password': data.get('password'),
            'phone': phone,  # Store formatted phone
            'position': data.get('position'),
            'province': data.get('province'),  # Store province
            'district': data.get('district'),  # Store district
            'officer_type': data.get('officer_type'),  # 'road' or 'garbage'
            'officer_region': data.get('officer_region'),  # Region/MC/UC
            'securityCode': data.get('securityCode')
        }

        
        # Check if email already exists
        if User.query.filter_by(email=signup_data['email']).first():
            return format_error_response('Email already exists')
        
        # Store pending signup
        pending_signups[phone] = signup_data
        
        # Send OTP
        print(f"🔄 Sending OTP to: {phone}")
        success, message = send_otp_to_phone(phone)
        
        if success:
            print(f"✅ OTP sent successfully to {phone}")
            return format_success_response({'phone': phone}, 'OTP sent successfully')
        else:
            print(f"❌ Failed to send OTP: {message}")
            return format_error_response(message)
    
    except Exception as e:
        print(f"❌ Error in send_otp: {str(e)}")
        traceback.print_exc()
        return format_error_response(f'Failed to send OTP: {str(e)}', 500)


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp_endpoint():
    """Verify OTP and return signup data for confirmation"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        otp = data.get('otp')
        
        if not phone or not otp:
            return format_error_response('Phone and OTP are required')
        
        # Format phone number to match send_otp format
        original_phone = phone
        if phone.startswith('0'):
            phone = '+94' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+94' + phone
        
        print(f"📱 Verifying OTP for: {original_phone} → {phone}")
        print(f"🔐 OTP entered: {otp}")
        print(f"📦 OTP storage keys: {list(otp_storage.keys())}")
        
        # Verify OTP
        success, message = verify_otp(phone, otp)
        
        if success:
            # Get pending signup data
            signup_data = pending_signups.get(phone)
            if not signup_data:
                return format_error_response('Signup session expired')
            
            return format_success_response({
                'verified': True,
                'userData': {
                    'name': signup_data['name'],
                    'email': signup_data['email'],
                    'phone': signup_data['phone'],
                    'position': signup_data['position']
                }
            }, 'OTP verified successfully')
        else:
            return format_error_response(message)
    
    except Exception as e:
        return format_error_response(f'OTP verification failed: {str(e)}', 500)


@auth_bp.route('/complete-signup', methods=['POST'])
def complete_signup():
    """Complete signup after OTP verification and profile confirmation"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return format_error_response('Phone number is required')
        
        # Format phone number to match send_otp format
        original_phone = phone
        if phone.startswith('0'):
            phone = '+94' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+94' + phone
        
        print(f"📱 Complete signup for: {original_phone} → {phone}")
        print(f"📦 Pending signups keys: {list(pending_signups.keys())}")
        
        # Get pending signup data
        signup_data = pending_signups.get(phone)
        if not signup_data:
            return format_error_response('Signup session expired')
        
        # Update with confirmed data (allow edits from confirmation screen)
        signup_data['name'] = data.get('name', signup_data.get('name'))
        signup_data['email'] = data.get('email', signup_data.get('email'))
        signup_data['phone'] = data.get('phone', signup_data.get('phone'))
        signup_data['position'] = data.get('position', signup_data.get('position'))
        signup_data['province'] = data.get('province', signup_data.get('province'))
        signup_data['district'] = data.get('district', signup_data.get('district'))
        
        # Determine if this is an officer signup
        # Officers have securityCode or officer_type
        is_officer = bool(signup_data.get('securityCode') or signup_data.get('officer_type'))
        
        print(f"🔍 Is officer signup: {is_officer}")
        
        if is_officer:
            # OFFICER SIGNUP
            # Extract province and district from position string
            # Format: "Chief Engineer - RDD (Western Province, Colombo)"
            officer_province = None
            officer_district = None
            position_str = signup_data.get('position', '')
            
            if '(' in position_str and ')' in position_str:
                # Extract text between parentheses
                location_part = position_str[position_str.find('(')+1:position_str.find(')')]
                # Split by comma
                parts = [p.strip() for p in location_part.split(',')]
                if len(parts) >= 2:
                    officer_province = parts[0]
                    officer_district = parts[1]
            
            print(f"👮 Creating officer: {signup_data['name']}")
            print(f"📍 Officer location: {officer_province}, {officer_district}")
            
            new_user = User(
                username=signup_data['name'],
                email=signup_data['email'],
                password_hash=hash_password(signup_data['password']),
                mobile=signup_data['phone'],
                position=signup_data['position'],
                is_officer=True,
                officer_province=officer_province,
                officer_district=officer_district,
                officer_region=signup_data.get('officer_region'),
                officer_type=signup_data.get('officer_type'),
                officer_title=signup_data.get('position')
            )
        else:
            # REGULAR USER SIGNUP
            # Use province/district directly from signup data
            user_province = signup_data.get('province')
            user_district = signup_data.get('district')
            
            print(f"👤 Creating regular user: {signup_data['name']}")
            print(f"📍 User location: {user_province}, {user_district}")
            
            new_user = User(
                username=signup_data['name'],
                email=signup_data['email'],
                password_hash=hash_password(signup_data['password']),
                mobile=signup_data['phone'],
                province=user_province,
                district=user_district,
                position=signup_data.get('position'),  # Optional for users
                is_officer=False
            )
        
        db.session.add(new_user)
        db.session.commit()
        
        print(f"✅ User created successfully: ID={new_user.id}, is_officer={new_user.is_officer}")
        
        # Clean up pending signup
        del pending_signups[phone]
        
        # Generate token
        token = generate_token(new_user.id)
        
        return format_success_response({
            'user': new_user.to_dict(),
            'token': token
        }, 'Signup completed successfully')
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Signup failed: {str(e)}")
        traceback.print_exc()
        return format_error_response(f'Signup failed: {str(e)}', 500)


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP to phone number"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return format_error_response('Phone number is required')
        
        # Format phone number to match send_otp format
        original_phone = phone
        if phone.startswith('0'):
            phone = '+94' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+94' + phone
        
        print(f"📱 Resending OTP for: {original_phone} → {phone}")
        
        # Check if there's a pending signup
        if phone not in pending_signups:
            return format_error_response('No pending signup found')
        
        # Send new OTP
        success, message = send_otp_to_phone(phone)
        
        if success:
            return format_success_response({'phone': phone}, 'OTP resent successfully')
        else:
            return format_error_response(message)
    
    except Exception as e:
        return format_error_response(f'Failed to resend OTP: {str(e)}', 500)
