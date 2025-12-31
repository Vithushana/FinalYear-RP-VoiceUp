"""
Component Service - Standalone Flask Server
============================================
This runs Harish's validation component as a separate service on port 5001.
The main application backend (port 5000) calls this service via HTTP.

This keeps the component completely isolated and makes it easy to:
- Run/stop independently
- Deploy separately
- Integrate with other team members' components
- Test in isolation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add component_harish directory to path
COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, COMPONENT_DIR)

# Import the validation functions
try:
    from working_demo import analyze_content as analyze_road
    from garbage_reporting_app import analyze_content as analyze_garbage
    COMPONENT_LOADED = True
    print("✅ Components loaded successfully (working_demo.py + garbage_reporting_app.py)")
except ImportError as e:
    print(f"❌ Failed to load component: {e}")
    COMPONENT_LOADED = False
    analyze_road = None
    analyze_garbage = None

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

def create_simple_notification_message(validation_result):
    """
    Convert validation result to simple, user-friendly notification message
    
    Removes technical terms like "Component 1" and makes it clear for users.
    Also disables actual strikes (just shows in popup, doesn't block user).
    """
    final_decision = validation_result.get('final_decision', {})
    status = final_decision.get('status', 'UNKNOWN')
    
    # Map status to simple notification message
    if status == 'ACCEPTED':
        return {
            'title': '✅ Post Approved',
            'message': 'Your report has been approved and will be submitted.',
            'type': 'success'
        }
    
    elif status == 'PRIVACY_PROTECTED':
        return {
            'title': '🛡️ Privacy Issue',
            'message': 'Your post was rejected because a human face or person was detected in the image.',
            'type': 'warning'
        }
    
    elif 'ABUSIVE IMAGE' in status:
        return {
            'title': '⚠️ Inappropriate Content',
            'message': 'Your post was rejected because the image contains inappropriate or dangerous items.',
            'type': 'warning'
        }
    
    elif 'ABUSIVE TEXT' in status:
        return {
            'title': '⚠️ Inappropriate Language',
            'message': 'Your post was rejected because the description contains inappropriate language.',
            'type': 'warning'
        }
    
    elif 'NOT A ROAD' in status or 'NOT ROAD' in status:
        return {
            'title': '📸 Not a Road Image',
            'message': 'Your post was rejected because the image does not show a road or street problem.',
            'type': 'warning'
        }
    
    elif 'GARBAGE' in status and 'NOT' not in status:
        return {
            'title': '🗑️ Garbage Detected',
            'message': 'The image shows garbage or waste material.',
            'type': 'info'
        }
    
    else:
        return {
            'title': '❌ Post Rejected',
            'message': 'Your post could not be processed. Please try again.',
            'type': 'error'
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'component': 'Harish Validation Component',
        'loaded': COMPONENT_LOADED,
        'version': '1.0'
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Main validation endpoint
    
    Request body:
    {
        "image": "base64_encoded_image",
        "description": "text description",
        "issue_type": "road" or "garbage"
    }
    
    Returns:
    {
        "flutter_response": { ... },
        "final_decision": { ... },
        "simple_notification": { ... },  # NEW - Simple message for notifications
        ...
    }
    """
    try:
        if not COMPONENT_LOADED:
            return jsonify({
                'flutter_response': {
                    'success': False,
                    'can_proceed': False,
                    'title': '❌ Component Not Loaded',
                    'message': 'The validation component failed to load',
                    'detailed_explanation': 'The component models could not be initialized. Check server logs.',
                    'what_to_do_next': 'Contact support to restart the validation service.',
                    'status_code': 'ERROR',
                    'component_name': 'Content Moderation & Safety Check',
                    'component_number': 1,
                    'total_components': 4
                },
                'final_decision': {
                    'status': 'ERROR',
                    'accepted': False,
                    'reason': 'Component not loaded',
                    'strike_issued': False  # Strikes disabled
                },
                'simple_notification': {
                    'title': '❌ System Error',
                    'message': 'Validation service is unavailable. Please try again later.',
                    'type': 'error'
                }
            }), 500
        
        data = request.get_json()
        
        # Validate request
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        image_data = data.get('image', '')
        description = data.get('description', '')
        issue_type = data.get('issue_type', 'road')
        
        print(f"\n{'='*60}")
        print(f"📥 VALIDATION REQUEST RECEIVED")
        print(f"{'='*60}")
        print(f"Issue Type: {issue_type}")
        print(f"Description: {description[:50]}..." if len(description) > 50 else f"Description: {description}")
        print(f"Image Data Length: {len(image_data)} characters")
        print(f"{'='*60}\n")
        
        # Call the appropriate validation function based on issue type
        issue_type_lower = issue_type.lower() if issue_type else 'road'
        if issue_type_lower == 'garbage':
            print(f"🗑️ Using garbage validation function")
            result = analyze_garbage(image_data, description)
        else:
            print(f"🛣️ Using road validation function")
            result = analyze_road(image_data, description)
        
        # DISABLE STRIKES: Set strike_issued to False always
        if 'final_decision' in result:
            result['final_decision']['strike_issued'] = False
        
        # Add simple notification message
        result['simple_notification'] = create_simple_notification_message(result)
        
        print(f"\n{'='*60}")
        print(f"📤 VALIDATION RESULT")
        print(f"{'='*60}")
        print(f"Status: {result.get('final_decision', {}).get('status', 'UNKNOWN')}")
        print(f"Accepted: {result.get('final_decision', {}).get('accepted', False)}")
        print(f"Strike Issued: {result.get('final_decision', {}).get('strike_issued', False)} (DISABLED)")
        print(f"{'='*60}\n")
        
        return jsonify(result), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'flutter_response': {
                'success': False,
                'can_proceed': False,
                'title': '❌ Component Error',
                'message': 'An error occurred in the validation component',
                'detailed_explanation': f'Error: {str(e)}',
                'what_to_do_next': 'Please try again. If the problem persists, contact support.',
                'status_code': 'ERROR',
                'component_name': 'Content Moderation & Safety Check',
                'component_number': 1,
                'total_components': 4
            },
            'final_decision': {
                'status': 'ERROR',
                'accepted': False,
                'reason': str(e),
                'strike_issued': False  # Strikes disabled for now
            },
            'simple_notification': {
                'title': '❌ Error',
                'message': 'An error occurred while validating your post. Please try again.',
                'type': 'error'
            }
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 STARTING COMPONENT SERVICE")
    print("="*60)
    print(f"Component: Harish's Validation Component")
    print(f"Port: 5001")
    print(f"Endpoints:")
    print(f"  - GET  /health  (Health check)")
    print(f"  - POST /analyze (Validation)")
    print(f"")
    print(f"⚠️  STRIKES DISABLED - Only shown in popup, users not blocked")
    print("="*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
