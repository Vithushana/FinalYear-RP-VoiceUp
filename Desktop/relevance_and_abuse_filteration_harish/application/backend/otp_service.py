import os
import random
from twilio.rest import Client
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio configuration - MUST be set in .env file
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Validate Twilio credentials
if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
    print("WARNING: Twilio credentials not configured. OTP service will not work.")
    print("Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in .env file")

# In-memory OTP storage (in production, use Redis or database)
otp_storage = {}

def generate_otp():
    """Generate a 4-digit OTP"""
    return str(random.randint(1000, 9999))

def send_otp_sms(phone_number, otp):
    """Send OTP via Twilio SMS"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message = client.messages.create(
            body=f'Your Voice Up verification code is: {otp}. Valid for 10 minutes.',
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        
        return True, message.sid
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False, str(e)

def store_otp(phone_number, otp):
    """Store OTP with expiration time"""
    expiration = datetime.now() + timedelta(minutes=10)
    otp_storage[phone_number] = {
        'otp': otp,
        'expires_at': expiration,
        'attempts': 0
    }

def verify_otp(phone_number, otp):
    """Verify OTP for a phone number"""
    if phone_number not in otp_storage:
        return False, "OTP not found or expired"
    
    stored_data = otp_storage[phone_number]
    
    # Check expiration
    if datetime.now() > stored_data['expires_at']:
        del otp_storage[phone_number]
        return False, "OTP expired"
    
    # Check attempts
    if stored_data['attempts'] >= 3:
        del otp_storage[phone_number]
        return False, "Too many failed attempts"
    
    # Verify OTP
    if stored_data['otp'] == otp:
        del otp_storage[phone_number]
        return True, "OTP verified successfully"
    else:
        stored_data['attempts'] += 1
        return False, "Invalid OTP"

def send_otp_to_phone(phone_number):
    """Generate and send OTP to phone number"""
    otp = generate_otp()
    store_otp(phone_number, otp)
    
    # Check if mock mode is enabled (for testing without Twilio SMS)
    mock_mode = os.getenv('OTP_MOCK_MODE', 'false').lower() == 'true'
    
    if mock_mode:
        print(f"\n{'='*50}")
        print(f"🔐 MOCK OTP MODE - OTP for {phone_number}: {otp}")
        print(f"{'='*50}\n")
        return True, f"OTP sent to {phone_number} (Mock Mode)"
    
    # Real Twilio SMS
    success, result = send_otp_sms(phone_number, otp)
    
    if success:
        return True, f"OTP sent to {phone_number}"
    else:
        # If Twilio fails, fall back to mock mode and print OTP
        print(f"\n{'='*50}")
        print(f"⚠️  Twilio SMS failed: {result}")
        print(f"🔐 FALLBACK - OTP for {phone_number}: {otp}")
        print(f"{'='*50}\n")
        return True, f"OTP generated (check backend console): {otp}"
