from flask import Blueprint, request, jsonify
from models import IssueModel, StatsModel
from functools import wraps
import jwt
import os

api = Blueprint('api', __name__)

def token_required(f):
    """Decorator to check for valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, os.getenv('JWT_SECRET', 'your-secret-key'), algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    return decorated

@api.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = StatsModel.get_dashboard_stats()
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching stats: {str(e)}'
        }), 500

@api.route('/issues', methods=['GET'])
def get_issues():
    """Get issues with optional filtering"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        status = request.args.get('status')
        
        issues = IssueModel.get_issues(limit=limit, skip=skip, status=status)
        return jsonify({
            'success': True,
            'data': issues,
            'count': len(issues)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching issues: {str(e)}'
        }), 500

@api.route('/issues/reposted', methods=['GET'])
def get_reposted_issues():
    """Get reposted issues"""
    try:
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        
        issues = IssueModel.get_reposted_issues(limit=limit, skip=skip)
        return jsonify({
            'success': True,
            'data': issues,
            'count': len(issues)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching reposted issues: {str(e)}'
        }), 500

@api.route('/issues/<issue_id>', methods=['GET'])
def get_issue_details(issue_id):
    """Get detailed information about a specific issue"""
    try:
        issue = IssueModel.get_issue_by_id(issue_id)
        if not issue:
            return jsonify({
                'success': False,
                'message': 'Issue not found'
            }), 404
        
        # Get matching/similar issues (for now, just get other issues by same type)
        matching_issues = IssueModel.get_issues(limit=6, skip=0)
        # Filter out the current issue
        matching_issues = [i for i in matching_issues if i['id'] != issue_id][:5]
        
        return jsonify({
            'success': True,
            'data': {
                'issue': issue,
                'matching_issues': matching_issues
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching issue details: {str(e)}'
        }), 500

@api.route('/issues', methods=['POST'])
@token_required
def create_issue():
    """Create a new issue"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['title', 'description', 'location', 'type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
        
        issue_id = IssueModel.create_issue(data)
        return jsonify({
            'success': True,
            'message': 'Issue created successfully',
            'issue_id': issue_id
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating issue: {str(e)}'
        }), 500

@api.route('/issues/<issue_id>/status', methods=['PUT'])
@token_required
def update_issue_status(issue_id):
    """Update issue status"""
    try:
        data = request.get_json()
        if not data or not data.get('status'):
            return jsonify({
                'success': False,
                'message': 'Status is required'
            }), 400
        
        valid_statuses = ['Seen', 'Verified', 'On Hold', 'In Progress', 'Completed']
        if data['status'] not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        success = IssueModel.update_issue_status(issue_id, data['status'])
        if success:
            # Update stats after status change
            StatsModel.update_stats()
            return jsonify({
                'success': True,
                'message': 'Issue status updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Issue not found or not updated'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating issue status: {str(e)}'
        }), 500

@api.route('/issues/search', methods=['GET'])
def search_issues():
    """Search issues by title, description, or location"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': False,
                'message': 'Search query is required'
            }), 400
        
        # For now, we'll do a simple text search
        # In production, you might want to use MongoDB text indexes
        from db import db
        issues_collection = db["issues"]
        
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"location": {"$regex": query, "$options": "i"}},
                {"type": {"$regex": query, "$options": "i"}}
            ]
        }
        
        cursor = issues_collection.find(search_query).sort("created_at", -1).limit(20)
        issues = []
        
        for issue in cursor:
            issue["_id"] = str(issue["_id"])
            issue["id"] = issue["_id"]
            issue["hasImage"] = len(issue.get("images", [])) > 0
            issue["image"] = issue.get("images", [None])[0]
            issues.append(issue)
        
        return jsonify({
            'success': True,
            'data': issues,
            'count': len(issues)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error searching issues: {str(e)}'
        }), 500

@api.route('/issues/<issue_id>/achievement', methods=['PUT'])
@token_required
def update_achievement(issue_id):
    """Update achievement for a completed issue"""
    try:
        data = request.get_json()
        if not data or not data.get('achievement'):
            return jsonify({
                'success': False,
                'message': 'Achievement text is required'
            }), 400
        
        success = IssueModel.update_achievement(issue_id, data['achievement'])
        if success:
            return jsonify({
                'success': True,
                'message': 'Achievement updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Issue not found or not updated'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating achievement: {str(e)}'
        }), 500