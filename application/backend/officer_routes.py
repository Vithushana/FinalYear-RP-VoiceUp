from flask import Blueprint, request, jsonify
from models import db, Post, User, OfficerReply
from utils import token_required, format_error_response, format_success_response, get_image_base64
from sqlalchemy import func, or_
from datetime import datetime, timedelta

officer_bp = Blueprint('officer', __name__, url_prefix='/api')

# ==================== DASHBOARD STATS ====================

@officer_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics for officers"""
    try:
        from models import Achievement
        
        # Get officer_id from query params (if provided)
        officer_id = request.args.get('officer_id', type=int)
        
        # Build base query with officer filtering (same logic as get_issues)
        if officer_id:
            officer = User.query.get(officer_id)
            if officer and officer.is_officer:
                # Filter by officer's region AND type
                base_query = Post.query.filter_by(
                    province=officer.officer_province,
                    district=officer.officer_district,
                    region=officer.officer_region
                )
                
                # CRITICAL: Also filter by issue type to match officer's department
                # NOTE: officer_type is lowercase but issue_type is capitalized
                if officer.officer_type:
                    issue_type_filter = officer.officer_type.capitalize()
                    base_query = base_query.filter_by(issue_type=issue_type_filter)
                    
                print(f"📊 Stats filtered for Officer {officer.username} (Type: {officer.officer_type} -> {issue_type_filter if officer.officer_type else 'None'})")
            else:
                base_query = Post.query
        else:
            base_query = Post.query
        
        # Total issues (filtered)
        total_issues = base_query.count()
        
        # Issues by status (filtered)
        submitted = base_query.filter_by(status='submitted').count()
        seen = base_query.filter_by(status='seen').count()
        verified = base_query.filter_by(status='verified').count()
        in_progress = base_query.filter_by(status='in_progress').count()
        completed = base_query.filter_by(status='completed').count()
        closed = base_query.filter_by(status='closed').count()
        on_hold = base_query.filter_by(status='hold').count()
        
        # Achievements count (filtered by officer region if officer_id provided)
        if officer_id and officer and officer.is_officer:
            # Count achievements in officer's region
            achievements_count = db.session.query(Achievement).join(Post).filter(
                Post.province == officer.officer_province,
                Post.district == officer.officer_district,
                Post.region == officer.officer_region
            ).count()
        else:
            achievements_count = Achievement.query.count()
        
        # Recent activity (last 7 days, filtered)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_issues = base_query.filter(Post.created_at >= week_ago).count()
        
        # Issues by type (filtered)
        issue_types = db.session.query(
            Post.issue_type,
            func.count(Post.id).label('count')
        ).filter(Post.id.in_([p.id for p in base_query.all()])).group_by(Post.issue_type).all()
        
        types_data = {issue_type: count for issue_type, count in issue_types}
        

        stats = {
            'total_issues': total_issues,
            'submitted': submitted,
            'unseen': submitted,  # Alias for submitted
            'seen': seen,
            'verified': verified,
            'in_progress': in_progress,
            'completed': completed,
            'closed': closed,
            'hold': on_hold,
            'on_hold': on_hold,  # Alias
            'recent_activity': recent_issues,
            'achievements': achievements_count,
            'issue_types': types_data
        }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return format_error_response(f'Error fetching stats: {str(e)}', 500)


# ==================== ISSUES MANAGEMENT ====================

@officer_bp.route('/issues', methods=['GET'])
def get_issues():
    """Get issues with optional filtering by officer region"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        status = request.args.get('status')
        officer_id = request.args.get('officer_id')  # NEW: Get officer ID from query params
        
        # Build query - filter by officer's region if officer_id provided
        if officer_id:
            officer = User.query.get(int(officer_id))
            if officer and officer.is_officer:
                # Filter by officer's region (province, district, region)
                query = Post.query.filter_by(
                    province=officer.officer_province,
                    district=officer.officer_district,
                    region=officer.officer_region
                )
                
                # CRITICAL: Filter by issue type to match officer's department
                # Garbage officers should only see Garbage posts
                # Road officers should only see Road posts
                # NOTE: officer_type is lowercase but issue_type is capitalized
                if officer.officer_type:
                    issue_type_filter = officer.officer_type.capitalize()
                    query = query.filter_by(issue_type=issue_type_filter)
            else:
                query = Post.query
        else:
            query = Post.query
        
        if status:
            # Map frontend status names to backend
            status_map = {
                'Seen': 'seen',
                'Verified': 'verified',
                'On Hold': 'hold',
                'In Progress': 'in_progress',
                'Completed': 'completed',
                'Submitted': 'submitted',
                'Closed': 'closed'  # Added for achievements/closed page
            }
            backend_status = status_map.get(status, status.lower())
            
            print(f"🔎 FILTER DEBUG:")
            print(f"   - Input Status: '{status}'")
            print(f"   - Mapped Status: '{backend_status}'")
            print(f"   - Officer Type: '{officer.officer_type if officer_id else 'None'}'")
            
            # Check counts before filter
            total_before = query.count()
            print(f"   - Posts before status filter: {total_before}")
            
            query = query.filter_by(status=backend_status)
            
            # Check counts after filter
            total_after = query.count()
            print(f"   - Posts after status filter: {total_after}")
            
            if total_after == 0 and total_before > 0:
                print(f"   ⚠️ WARNING: Status filter removed all posts!")
                # Debug check - are there ANY posts with this status?
                check = Post.query.filter_by(status=backend_status).count()
                print(f"   - Total posts in DB with status '{backend_status}': {check}")
        
        # Get posts
        posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
        
        # Format response
        issues = []
        for post in posts:
            issue = post.to_dict()
            # Convert images from filenames to base64
            images_base64 = []
            for img_filename in post.get_images():
                img_base64 = get_image_base64(img_filename)
                if img_base64:
                    images_base64.append(img_base64)
            issue['images'] = images_base64
            # Add fields expected by frontend
            issue['hasImage'] = len(images_base64) > 0
            issue['image'] = images_base64[0] if images_base64 else None
            issue['type'] = post.issue_type
            issue['reporter_name'] = post.author.username
            issue['time'] = _format_relative_time(post.created_at)
            issues.append(issue)
        
        return jsonify({
            'success': True,
            'data': issues,
            'count': len(issues)
        }), 200
        
    except Exception as e:
        return format_error_response(f'Error fetching issues: {str(e)}', 500)


@officer_bp.route('/issues/reposted', methods=['GET'])
def get_reposted_issues():
    """Get reposted issues (issues with citizen replies or retags) filtered by officer region"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        officer_id = request.args.get('officer_id')  # NEW: Get officer ID
        
        # Build base query
        query = Post.query.join(OfficerReply)
        
        # Filter by officer's region if officer_id provided
        if officer_id:
            officer = User.query.get(int(officer_id))
            if officer and officer.is_officer:
                query = query.filter(
                    Post.province == officer.officer_province,
                    Post.district == officer.officer_district,
                    Post.region == officer.officer_region
                )
                
                # CRITICAL: Filter by issue type to match officer's department
                if officer.officer_type:
                    query = query.filter(Post.issue_type == officer.officer_type)
        
        posts = query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
        
        # Format response
        issues = []
        for post in posts:
            issue = post.to_dict()
            # Convert images from filenames to base64
            images_base64 = []
            for img_filename in post.get_images():
                img_base64 = get_image_base64(img_filename)
                if img_base64:
                    images_base64.append(img_base64)
            issue['images'] = images_base64
            issue['hasImage'] = len(images_base64) > 0
            issue['image'] = images_base64[0] if images_base64 else None
            issue['type'] = post.issue_type
            issue['reporter_name'] = post.author.username
            issue['time'] = _format_relative_time(post.created_at)
            issues.append(issue)
        
        return jsonify({
            'success': True,
            'data': issues,
            'count': len(issues)
        }), 200
        
    except Exception as e:
        return format_error_response(f'Error fetching reposted issues: {str(e)}', 500)


@officer_bp.route('/issues/<int:issue_id>', methods=['GET'])
def get_issue_details(issue_id):
    """Get detailed information about a specific issue"""
    try:
        post = Post.query.get(issue_id)
        if not post:
            return format_error_response('Issue not found', 404)
        
        issue = post.to_dict()
        # Convert images from filenames to base64
        images_base64 = []
        for img_filename in post.get_images():
            img_base64 = get_image_base64(img_filename)
            if img_base64:
                images_base64.append(img_base64)
        issue['images'] = images_base64
        issue['hasImage'] = len(images_base64) > 0
        issue['image'] = images_base64[0] if images_base64 else None
        issue['type'] = post.issue_type
        issue['reporter_name'] = post.author.username
        issue['time'] = _format_relative_time(post.created_at)
        
        # Get matching/similar issues (same type)
        matching_posts = Post.query.filter(
            Post.issue_type == post.issue_type,
            Post.id != issue_id
        ).limit(5).all()
        
        matching_issues = []
        for match in matching_posts:
            match_data = match.to_dict()
            # Convert images from filenames to base64
            images_base64 = []
            for img_filename in match.get_images():
                img_base64 = get_image_base64(img_filename)
                if img_base64:
                    images_base64.append(img_base64)
            match_data['images'] = images_base64
            match_data['hasImage'] = len(images_base64) > 0
            match_data['image'] = images_base64[0] if images_base64 else None
            matching_issues.append(match_data)
        
        return jsonify({
            'success': True,
            'data': {
                'issue': issue,
                'matching_issues': matching_issues
            }
        }), 200
        
    except Exception as e:
        return format_error_response(f'Error fetching issue details: {str(e)}', 500)


# ==================== STATUS UPDATES ====================

@officer_bp.route('/issues/<int:issue_id>/status', methods=['PUT'])
# @token_required  # TODO: Enable when officer auth is ready
def update_issue_status(issue_id):
    """Update issue status - FIXED VERSION WITH NOTIFICATIONS"""
    print(f"\n🚀 UPDATE_ISSUE_STATUS CALLED (officer_routes.py) - Issue ID: {issue_id}")
    try:
        from notifications import notify_user_status_change, notify_region_officers_status_change
        from models import Achievement
        
        data = request.get_json()
        if not data or not data.get('status'):
            return format_error_response('Status is required', 400)
        
        # Map frontend status to backend
        status_map = {
            'Seen': 'seen',
            'Verified': 'verified',
            'On Hold': 'hold',
            'In Progress': 'in_progress',
            'Completed': 'completed',
            'Submitted': 'submitted'
        }
        
        new_status = status_map.get(data['status'], data['status'].lower())
        print(f"   Requested status change to: {new_status}")
        
        post = Post.query.get(issue_id)
        if not post:
            return format_error_response('Issue not found', 404)
        
        old_status = post.status
        post.status = new_status
        post.updated_at = datetime.utcnow()
        
        # Handle completion timestamp
        if new_status == 'completed' and old_status != 'completed':
            post.completed_at = datetime.utcnow()
        
        # Handle closed status - create achievement
        if new_status == 'closed' and old_status != 'closed':
            post.closed_at = datetime.utcnow()
            
            # Create achievement record
            try:
                # Get first image as before_image
                images = post.get_images()
                before_image = images[0] if images else None
                
                # Check if achievement already exists
                existing_achievement = Achievement.query.filter_by(post_id=post.id).first()
                if not existing_achievement:
                    achievement = Achievement(
                        post_id=post.id,
                        description=post.description,
                        location=post.location,
                        posted_date=post.created_at.date() if post.created_at else None,
                        completed_date=post.completed_at.date() if post.completed_at else datetime.utcnow().date(),
                        before_image=before_image,
                        after_image=post.completion_image,
                        officer_id=post.assigned_officer_id
                    )
                    db.session.add(achievement)
                    print(f"✅ Created achievement for post {issue_id}")
            except Exception as e:
                print(f"⚠️ Failed to create achievement: {str(e)}")
        
        db.session.commit()
        
        print(f"✅ Post {issue_id} status: {old_status} → {new_status}")
        
        # 🔔 CRITICAL: Notify users AFTER commit
        print(f"\n{'='*60}")
        print(f"🔔 NOTIFICATION PROCESS STARTING")
        print(f"{'='*60}")
        
        # Notify ALL officers in the region about status change
        print(f"\n🔔 Step 1: Notifying peer officers...")
        try:
            changing_officer_id = data.get('officer_id')
            officers_notified = notify_region_officers_status_change(post, new_status, changing_officer_id)
            print(f"   ✅ Notified {officers_notified} peer officers")
        except Exception as e:
            print(f"   ⚠️ Failed to notify officers: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Send notification to user about status change
        print(f"\n🔔 Step 2: Notifying user...")
        try:
            notify_user_status_change(post, new_status)
            print(f"   ✅ User notification sent")
        except Exception as e:
            print(f"   ⚠️ Failed to notify user: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"{'='*60}\n")
        
        return jsonify({
            'success': True,
            'message': 'Issue status updated successfully'
        }), 200
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR in update_issue_status:")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        db.session.rollback()
        return format_error_response(f'Error updating issue status: {str(e)}', 500)


# ==================== SEARCH ====================

@officer_bp.route('/issues/search', methods=['GET'])
def search_issues():
    """Search issues by title, description, or location"""
    try:
        query_text = request.args.get('q', '').strip()
        if not query_text:
            return format_error_response('Search query is required', 400)
        
        # Search in title, description, location, issue_type
        search_filter = or_(
            Post.title.ilike(f'%{query_text}%'),
            Post.description.ilike(f'%{query_text}%'),
            Post.location.ilike(f'%{query_text}%'),
            Post.issue_type.ilike(f'%{query_text}%')
        )
        
        posts = Post.query.filter(search_filter).order_by(Post.created_at.desc()).limit(20).all()
        
        issues = []
        for post in posts:
            issue = post.to_dict()
            issue['hasImage'] = len(post.get_images()) > 0
            issue['image'] = post.get_images()[0] if post.get_images() else None
            issue['type'] = post.issue_type
            issue['reporter_name'] = post.author.username
            issues.append(issue)
        
        return jsonify({
            'success': True,
            'data': issues,
            'count': len(issues)
        }), 200
        
    except Exception as e:
        return format_error_response(f'Error searching issues: {str(e)}', 500)


# ==================== OFFICER REPLIES ====================

@officer_bp.route('/issues/<int:issue_id>/reply', methods=['POST'])
# @token_required  # TODO: Enable when officer auth is ready
def add_officer_reply(issue_id):
    """Add officer reply to an issue"""
    try:
        data = request.get_json()
        if not data or not data.get('message'):
            return format_error_response('Message is required', 400)
        
        post = Post.query.get(issue_id)
        if not post:
            return format_error_response('Issue not found', 404)
        
        # Create officer reply
        reply = OfficerReply(
            post_id=issue_id,
            officer_id=1,  # TODO: Get from token
            department=data.get('department', 'Road Development Authority (RDA)'),
            message=data['message']
        )
        
        db.session.add(reply)
        db.session.commit()
        
        # Notify user about officer reply
        try:
            from notifications import create_notification
            create_notification(
                user_id=post.user_id,
                title='Officer Reply',
                message=f'Officer from {reply.department} replied: {reply.message[:50]}...',
                notification_type='officer_reply',
                post_id=post.id,
                action_url=f'/my-requests/{post.id}'
            )
            print(f"✅ Notified user {post.user_id} about officer reply")
        except Exception as e:
            print(f"⚠️ Failed to notify user about officer reply: {str(e)}")
        
        return jsonify({
            'success': True,
            'message': 'Reply added successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Error adding reply: {str(e)}', 500)


# ==================== HELPER FUNCTIONS ====================

def _format_relative_time(dt):
    """Format datetime as relative time (e.g., '2 hours ago')"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return "Just now"