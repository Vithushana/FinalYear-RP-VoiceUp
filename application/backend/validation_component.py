"""
Multi-Component Validation Integration (External Services)
===========================================================
Calls multiple validation components as separate Flask services via HTTP.
All components run in PARALLEL for speed.

Priority System:
- Component 1 (Harish) runs first priority checks
- Component 2 (AI Detection) runs ONLY for ROAD issues
- Component 2 (Garbage Classification) runs BEFORE validation (during image selection)
- Component 1 rejection reasons take precedence over Component 2

Architecture:
- Component 1 (Harish): http://localhost:5001 - Privacy, Relevance, Abuse, Text
- Component 2 (Dual Service): http://localhost:5002
  - /analyze - AI vs Real (for ROAD issues only)
  - /classify - Garbage Type (called separately during image selection for GARBAGE)
- Component 3 (Garbage Identification): http://localhost:5003 - Terminal-only detailed detection
- Main application backend: http://localhost:5000
"""

import requests
import os
import concurrent.futures

# ============================================================
# TEMPORARY DISABLE FLAGS - Set to True to skip a component
# ============================================================
DISABLE_COMPONENT_1 = True   # Component 1 (Harish) - Privacy/Abuse/Relevance
DISABLE_COMPONENT_2 = True   # Component 2 (Vithushana) - AI Detection/Garbage
# ============================================================

# Component service configuration
COMPONENT_1_URL = os.getenv('COMPONENT_1_URL', 'http://localhost:5001/analyze')
COMPONENT_2_AI_URL = os.getenv('COMPONENT_2_AI_URL', 'http://localhost:5002/analyze')
COMPONENT_2_GARBAGE_URL = os.getenv('COMPONENT_2_GARBAGE_URL', 'http://localhost:5002/classify')
COMPONENT_3_GARBAGE_IDENTIFY_URL = os.getenv('COMPONENT_3_GARBAGE_IDENTIFY_URL', 'http://localhost:5003/predict')
COMPONENT_TIMEOUT = 60  # seconds


def call_component_service(url, image_data, description, issue_type, component_name):
    """
    Call a component service via HTTP
    
    Args:
        url: Component service URL
        image_data: Base64 encoded image
        description: Text description
        issue_type: 'road' or 'garbage'
        component_name: Name for logging
    
    Returns:
        Component response dict or error dict
    """
    try:
        payload = {
            'image': image_data,
            'description': description,
            'issue_type': issue_type
        }
        
        print(f"📡 Calling {component_name} at {url}")
        
        response = requests.post(
            url,
            json=payload,
            timeout=COMPONENT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {component_name} responded successfully")
            return result
        else:
            print(f"❌ {component_name} error: {response.status_code}")
            return {
                'error': True,
                'status_code': response.status_code,
                'component': component_name
            }
    
    except requests.exceptions.Timeout:
        print(f"⏱️ {component_name} timeout")
        return {
            'error': True,
            'reason': 'timeout',
            'component': component_name
        }
    
    except requests.exceptions.ConnectionError:
        print(f"🔌 Cannot connect to {component_name}")
        return {
            'error': True,
            'reason': 'connection_error',
            'component': component_name
        }
    
    except Exception as e:
        print(f"❌ {component_name} unexpected error: {e}")
        return {
            'error': True,
            'reason': str(e),
            'component': component_name
        }


def detect_garbage_types_terminal(image_data: str):
    """
    Detect detailed garbage types and show results in terminal only
    Called for GARBAGE issues when issue_type is 'garbage'
    
    Args:
        image_data: Base64 encoded image
        
    Returns:
        None (results printed to terminal only)
    """
    try:
        payload = {'image': image_data}
        
        print(f"\n{'='*50}")
        print(f"🗑️ DETAILED GARBAGE TYPE DETECTION")
        print(f"{'='*50}")
        print(f"📡 Calling Garbage Identification Service...")
        
        response = requests.post(
            COMPONENT_3_GARBAGE_IDENTIFY_URL,
            json=payload,
            timeout=COMPONENT_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            detections = result.get('detections', [])
            best_prediction = result.get('best_prediction')
            
            print(f"✅ Garbage detection completed!")
            print(f"📊 Found {len(detections)} garbage items:")
            
            if detections:
                for i, detection in enumerate(detections, 1):
                    class_name = detection.get('class_name', 'Unknown')
                    confidence = detection.get('confidence', 0)
                    print(f"   {i}. {class_name} (Confidence: {confidence:.2f})")
                
                if best_prediction:
                    best_name = best_prediction.get('class_name', 'Unknown')
                    best_conf = best_prediction.get('confidence', 0)
                    print(f"\n🎯 BEST MATCH: {best_name} (Confidence: {best_conf:.2f})")
            else:
                print(f"   No garbage detected in image")
                
        else:
            print(f"❌ Garbage detection service error: {response.status_code}")
            
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"❌ Error calling garbage detection: {e}")
        print(f"{'='*50}\n")


def validate_post_content(image_data: str, description: str, issue_type: str):
    """
    Validate post content by calling multiple components in PARALLEL
    
    Flow Based on Issue Type:
    
    FOR ROAD ISSUES:
    1. Component 1 (Harish) checks: Privacy, Relevance, Abuse, Text
    2. Component 2 (AI Detection) checks: AI vs Real image
    3. If Component 1 REJECTS → Show Component 1 reasons
    4. If Component 1 PASSES but Component 2 REJECTS → Show Component 2 reasons
    5. If both PASS → APPROVED
    
    FOR GARBAGE ISSUES:
    1. Component 2 (Garbage Classification) already ran during image selection
       (auto-filled garbage_type field)
    2. Component 1 (Harish) runs validation: Privacy, Abuse, Text
    3. Component 3 (Garbage Identification) runs in parallel for terminal display
    4. If Component 1 REJECTS → Show Component 1 reasons
    5. If Component 1 PASSES → APPROVED
    
    Args:
        image_data: Base64 encoded image
        description: Text description
        issue_type: 'road' or 'garbage'
    
    Returns:
        Combined validation result with flutter_response format
    """
    
    print(f"\n{'='*60}")
    print(f"🔄 VALIDATION STARTED")
    print(f"{'='*60}")
    print(f"Issue Type: {issue_type}")
    print(f"{'='*60}\n")
    
    # Normalize issue_type to lowercase for comparison
    issue_type_lower = issue_type.lower() if issue_type else 'road'

    # Build auto-pass result used when a component is disabled
    def auto_pass():
        return {
            'final_decision': {'accepted': True, 'status': 'ACCEPTED', 'strike_issued': False},
            'flutter_response': {'success': True, 'can_proceed': True, 'title': '✅ Approved', 'message': 'Validation passed', 'status_code': 'APPROVED'}
        }

    if issue_type_lower == 'road':
        # ROAD ISSUE: Run both Component 1 and Component 2 (AI Detection) in parallel
        print(f"📍 ROAD Issue: Running Component 1 + Component 2 (AI Detection) in parallel")
        print(f"   Component 1 disabled: {DISABLE_COMPONENT_1}")
        print(f"   Component 2 disabled: {DISABLE_COMPONENT_2}")

        if DISABLE_COMPONENT_1:
            component_1_result = auto_pass()
            print(f"⏭️  Component 1 SKIPPED (disabled)")
        if DISABLE_COMPONENT_2:
            component_2_result = auto_pass()
            print(f"⏭️  Component 2 SKIPPED (disabled)")

        if not DISABLE_COMPONENT_1 or not DISABLE_COMPONENT_2:
            workers = (0 if DISABLE_COMPONENT_1 else 1) + (0 if DISABLE_COMPONENT_2 else 1)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max(workers, 1)) as executor:
                if not DISABLE_COMPONENT_1:
                    future_component_1 = executor.submit(
                        call_component_service, COMPONENT_1_URL, image_data, description, issue_type, "Component 1 (Harish)"
                    )
                if not DISABLE_COMPONENT_2:
                    future_component_2 = executor.submit(
                        call_component_service, COMPONENT_2_AI_URL, image_data, description, issue_type, "Component 2 (AI Detection)"
                    )
                if not DISABLE_COMPONENT_1:
                    component_1_result = future_component_1.result()
                if not DISABLE_COMPONENT_2:
                    component_2_result = future_component_2.result()

        print(f"\n{'='*60}")
        print(f"✅ PARALLEL VALIDATION COMPLETE")
        print(f"{'='*60}\n")

        # Check for errors
        if component_1_result.get('error'):
            return create_error_response("Component 1 unavailable", component_1_result.get('reason', 'unknown'))
        
        if component_2_result.get('error'):
            return create_error_response("Component 2 unavailable", component_2_result.get('reason', 'unknown'))
        
        # Apply priority logic
        component_1_accepted = component_1_result.get('final_decision', {}).get('accepted', False)
        component_2_accepted = component_2_result.get('final_decision', {}).get('accepted', False)
        
        print(f"📊 RESULTS:")
        print(f"   Component 1 (Harish): {'✅ PASS' if component_1_accepted else '❌ FAIL'}")
        print(f"   Component 2 (AI Detection): {'✅ PASS' if component_2_accepted else '❌ FAIL'}")
        print()
        
        # Priority Logic Implementation
        if not component_1_accepted:
            print(f"🎯 FINAL DECISION: Component 1 rejected → Using Component 1 reasons")
            return component_1_result
        
        elif not component_2_accepted:
            print(f"🎯 FINAL DECISION: Component 1 passed, Component 2 rejected → Using Component 2 reasons")
            return component_2_result
        
        else:
            print(f"🎯 FINAL DECISION: Both components passed → APPROVED")
            return component_1_result
    
    else:
        # GARBAGE ISSUE: Run Component 1 + Terminal Garbage Detection in parallel
        print(f"🗑️ GARBAGE Issue: Running Component 1 + Terminal Garbage Detection in parallel")
        print(f"   Component 1 disabled: {DISABLE_COMPONENT_1}")

        if DISABLE_COMPONENT_1:
            component_1_result = auto_pass()
            print(f"⏭️  Component 1 SKIPPED (disabled)")
            detect_garbage_types_terminal(image_data)
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_component_1 = executor.submit(
                    call_component_service,
                    COMPONENT_1_URL,
                    image_data,
                    description,
                    issue_type,
                    "Component 1 (Harish)"
                )
                
                future_garbage_detect = executor.submit(
                    detect_garbage_types_terminal,
                    image_data
                )
                
                component_1_result = future_component_1.result()
                future_garbage_detect.result()  # Just for terminal output
        
        print(f"\n{'='*60}")
        print(f"✅ VALIDATION COMPLETE")
        print(f"{'='*60}\n")
        
        # Check for errors
        if component_1_result.get('error'):
            return create_error_response("Component 1 unavailable", component_1_result.get('reason', 'unknown'))
        
        component_1_accepted = component_1_result.get('final_decision', {}).get('accepted', False)
        
        print(f"📊 RESULTS:")
        print(f"   Component 1 (Harish): {'✅ PASS' if component_1_accepted else '❌ FAIL'}")
        print()
        
        if not component_1_accepted:
            print(f"🎯 FINAL DECISION: Component 1 rejected → Using Component 1 reasons")
        else:
            print(f"🎯 FINAL DECISION: Component 1 passed → APPROVED")
        
        return component_1_result


def classify_garbage(image_data: str):
    """
    Classify garbage type using Component 2
    Called during image selection for GARBAGE issues
    
    Args:
        image_data: Base64 encoded image
        
    Returns:
        Classification result dict
    """
    # Call the classify endpoint on port 5002 (Dual service)
    return call_component_service(
        COMPONENT_2_GARBAGE_URL,
        image_data,
        "",
        "garbage",
        "Component 2 (Garbage Classification)"
    )


def create_error_response(title, reason):
    """Create error response when component service is unavailable"""
    return {
        'flutter_response': {
            'success': False,
            'can_proceed': False,
            'title': f'❌ {title}',
            'message': 'A validation service is currently unavailable',
            'detailed_explanation': f'Error: {reason}',
            'what_to_do_next': 'Please try again later or contact support.',
            'status_code': 'SERVICE_UNAVAILABLE',
            'component_name': 'Validation System',
            'component_number': 0,
            'total_components': 4
        },
        'final_decision': {
            'status': 'SERVICE_UNAVAILABLE',
            'accepted': False,
            'reason': reason,
            'strike_issued': False
        },
        'simple_notification': {
            'title': '❌ Service Unavailable',
            'message': 'Validation service is temporarily unavailable. Please try again.',
            'type': 'error'
        }
    }