"""
Component Integration Module
Handles parallel processing of 4 components for post validation
"""

import time
import threading
from typing import Dict, Any
import sys
import os

# Add parent directory to path to import your component
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def component_1_relevance_abuse(image_data: str, description: str) -> Dict[str, Any]:
    """
    Component 1: Relevance and Abuse Filtration (Harish's Component)
    
    This will call your existing working_demo.py analyze_content function
    For now, it's a placeholder that always passes
    
    Args:
        image_data: Base64 encoded image
        description: Text description
    
    Returns:
        Dict with status, reason, confidence, details
    """
    try:
        # TODO: Import and call your actual component
        # from working_demo import analyze_content
        # result = analyze_content(image_data, description)
        
        # Placeholder implementation
        time.sleep(0.5)  # Simulate processing
        
        return {
            'status': 'passed',
            'reason': 'Component 1: Relevance and abuse check passed',
            'confidence': 0.95,
            'details': {
                'component': 'Relevance & Abuse Filtration',
                'road_detected': True,
                'abuse_detected': False,
                'human_detected': False,
                'text_abuse': False
            }
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'reason': f'Component 1 error: {str(e)}',
            'confidence': 0.0,
            'details': {'error': str(e)}
        }


def component_2_placeholder(image_data: str, description: str) -> Dict[str, Any]:
    """
    Component 2: Placeholder (To be implemented later)
    
    Args:
        image_data: Base64 encoded image
        description: Text description
    
    Returns:
        Dict with status, reason, confidence, details
    """
    try:
        time.sleep(0.3)  # Simulate processing
        
        return {
            'status': 'passed',
            'reason': 'Component 2: Placeholder check passed',
            'confidence': 1.0,
            'details': {
                'component': 'Component 2 (Placeholder)',
                'note': 'This component will be implemented later'
            }
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'reason': f'Component 2 error: {str(e)}',
            'confidence': 0.0,
            'details': {'error': str(e)}
        }


def component_3_placeholder(image_data: str, description: str) -> Dict[str, Any]:
    """
    Component 3: Placeholder (To be implemented later)
    
    Args:
        image_data: Base64 encoded image
        description: Text description
    
    Returns:
        Dict with status, reason, confidence, details
    """
    try:
        time.sleep(0.4)  # Simulate processing
        
        return {
            'status': 'passed',
            'reason': 'Component 3: Placeholder check passed',
            'confidence': 1.0,
            'details': {
                'component': 'Component 3 (Placeholder)',
                'note': 'This component will be implemented later'
            }
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'reason': f'Component 3 error: {str(e)}',
            'confidence': 0.0,
            'details': {'error': str(e)}
        }


def component_4_placeholder(image_data: str, description: str) -> Dict[str, Any]:
    """
    Component 4: Placeholder (To be implemented later)
    
    Args:
        image_data: Base64 encoded image
        description: Text description
    
    Returns:
        Dict with status, reason, confidence, details
    """
    try:
        time.sleep(0.2)  # Simulate processing
        
        return {
            'status': 'passed',
            'reason': 'Component 4: Placeholder check passed',
            'confidence': 1.0,
            'details': {
                'component': 'Component 4 (Placeholder)',
                'note': 'This component will be implemented later'
            }
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'reason': f'Component 4 error: {str(e)}',
            'confidence': 0.0,
            'details': {'error': str(e)}
        }


def run_component_with_timeout(component_func, image_data, description, result_dict, component_name, timeout=60):
    """
    Run a component function with timeout
    
    Args:
        component_func: Component function to run
        image_data: Base64 encoded image
        description: Text description
        result_dict: Dictionary to store results
        component_name: Name of the component
        timeout: Timeout in seconds
    """
    def target():
        try:
            start_time = time.time()
            result = component_func(image_data, description)
            processing_time = time.time() - start_time
            
            result_dict[component_name] = {
                'result': result,
                'processing_time': processing_time
            }
        except Exception as e:
            result_dict[component_name] = {
                'result': {
                    'status': 'error',
                    'reason': f'Exception in {component_name}: {str(e)}',
                    'confidence': 0.0,
                    'details': {'error': str(e)}
                },
                'processing_time': 0.0
            }
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)
    
    if thread.is_alive():
        # Timeout occurred
        result_dict[component_name] = {
            'result': {
                'status': 'error',
                'reason': f'{component_name} timed out after {timeout} seconds',
                'confidence': 0.0,
                'details': {'error': 'timeout'}
            },
            'processing_time': timeout
        }


def process_components_parallel(image_data: str, description: str, timeout: int = 60) -> Dict[str, Any]:
    """
    Process all 4 components in parallel
    
    Args:
        image_data: Base64 encoded image
        description: Text description
        timeout: Timeout for each component in seconds
    
    Returns:
        Dict with:
            - all_passed: bool
            - results: dict of component results
            - total_time: float
            - summary: str
    """
    start_time = time.time()
    
    # Dictionary to store results from all threads
    results = {}
    
    # Component functions
    components = {
        'component_1_relevance_abuse': component_1_relevance_abuse,
        'component_2_placeholder': component_2_placeholder,
        'component_3_placeholder': component_3_placeholder,
        'component_4_placeholder': component_4_placeholder
    }
    
    # Create and start threads for each component
    threads = []
    for component_name, component_func in components.items():
        thread = threading.Thread(
            target=run_component_with_timeout,
            args=(component_func, image_data, description, results, component_name, timeout)
        )
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    # Check if all components passed
    all_passed = True
    failed_components = []
    
    for component_name, component_data in results.items():
        result = component_data['result']
        if result['status'] != 'passed':
            all_passed = False
            failed_components.append({
                'component': component_name,
                'reason': result['reason']
            })
    
    # Generate summary
    if all_passed:
        summary = 'All components passed validation'
    else:
        summary = f'{len(failed_components)} component(s) failed: ' + ', '.join([f['component'] for f in failed_components])
    
    return {
        'all_passed': all_passed,
        'results': results,
        'failed_components': failed_components,
        'total_time': total_time,
        'summary': summary
    }
