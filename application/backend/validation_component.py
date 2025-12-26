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
- Main application backend: http://localhost:5000
"""

import requests
import os
import concurrent.futures

# Component service configuration
COMPONENT_1_URL = os.getenv('COMPONENT_1_URL', 'http://localhost:5001/analyze')
COMPONENT_2_AI_URL = os.getenv('COMPONENT_2_AI_URL', 'http://localhost:5002/analyze')
COMPONENT_2_GARBAGE_URL = os.getenv('COMPONENT_2_GARBAGE_URL', 'http://localhost:5002/classify')
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
    2. Only Component 1 (Harish) runs validation: Privacy, Abuse, Text
    3. No AI detection for garbage (not needed)
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
    
    if issue_type_lower == 'road':
        # ROAD ISSUE: Run both Component 1 and Component 2 (AI Detection) in parallel
        print(f"📍 ROAD Issue: Running Component 1 + Component 2 (AI Detection) in parallel")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_component_1 = executor.submit(
                call_component_service,
                COMPONENT_1_URL,
                image_data,
                description,
                issue_type,
                "Component 1 (Harish)"
            )
            
            future_component_2 = executor.submit(
                call_component_service,
                COMPONENT_2_AI_URL,
                image_data,
                description,
                issue_type,
                "Component 2 (AI Detection)"
            )
            
            component_1_result = future_component_1.result()
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
        # GARBAGE ISSUE: Only run Component 1 (garbage classification already done)
        print(f"🗑️ GARBAGE Issue: Running Component 1 only (garbage type already classified)")
        
        component_1_result = call_component_service(
            COMPONENT_1_URL,
            image_data,
            description,
            issue_type,
            "Component 1 (Harish)"
        )
        
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

