"""
Additional API endpoints for location-based routing
Append these to posts.py
"""

# Add these imports at the top of posts.py if not already present
# from location_service import get_officer_stats, notify_status_change, notify_officer_reply

@posts_bp.route('/officer/<int:officer_id>', methods=['GET'])
def get_officer_posts(officer_id):
    """Get all posts in the officer's region (not just assigned to them)"""
    try:
        from location_service import get_officer_stats
        
        # Get the officer's details to find their region
        officer = User.query.get(officer_id)
        if not officer or not officer.is_officer:
            return format_error_response('Officer not found', 404)
        
        # Get query parameters
        status = request.args.get('status')  # Filter by status
        limit = request.args.get('limit', type=int, default=20)
        offset = request.args.get('offset', type=int, default=0)
        
        # Build query - filter by officer's region, province, and district
        query = Post.query.filter_by(
            province=officer.officer_province,
            district=officer.officer_district,
            region=officer.officer_region
        )
        
        # Filter by status if provided
        if status:
            query = query.filter_by(status=status)
        
        # Order by created_at descending (latest first)
        query = query.order_by(Post.created_at.desc())
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        posts = query.limit(limit).offset(offset).all()
        
        # Get officer stats (for the entire region)
        stats = get_officer_stats(officer_id)
        
        return format_success_response({
            'posts': [post.to_dict() for post in posts],
            'total_count': total_count,
            'stats': stats,
            'limit': limit,
            'offset': offset
        }, 'Posts retrieved successfully')
    
    except Exception as e:
        return format_error_response(f'Failed to get officer posts: {str(e)}', 500)


@posts_bp.route('/<int:post_id>/status', methods=['PUT'])
def update_post_status(post_id):
    """Update post status and notify user"""
    print(f"\n🚀 UPDATE_POST_STATUS CALLED - Post ID: {post_id}")
    try:
        from location_service import notify_status_change
        from notifications import notify_user_status_change
        from models import Achievement
        
        data = request.get_json()
        new_status = data.get('status')
        print(f"   Requested status change to: {new_status}")
        
        if not new_status:
            return format_error_response('Status is required')
        
        # Valid statuses
        valid_statuses = ['submitted', 'seen', 'verified', 'hold', 'in_progress', 'completed', 'closed']
        if new_status not in valid_statuses:
            return format_error_response(f'Invalid status. Must be one of: {", ".join(valid_statuses)}')
        
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
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
                    print(f"✅ Created achievement for post {post_id}")
            except Exception as e:
                print(f"⚠️ Failed to create achievement: {str(e)}")
        
        db.session.commit()
        
        print(f"✅ Post {post_id} status: {old_status} → {new_status}")
        
        # CRITICAL: Notify users AFTER commit, OUTSIDE try-except
        # Notify ALL officers in the region about status change
        print(f"\n🔔 Notifying officers about status change...")
        try:
            from notifications import notify_region_officers_status_change
            changing_officer_id = data.get('officer_id')  # Optional: passed from frontend
            officers_notified = notify_region_officers_status_change(post, new_status, changing_officer_id)
            print(f"   ✅ Notified {officers_notified} peer officers")
        except Exception as e:
            print(f"   ⚠️ Failed to notify region officers: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Send notification to user about status change
        print(f"\n🔔 Notifying user about status change...")
        try:
            from notifications import notify_user_status_change
            notify_user_status_change(post, new_status)
            print(f"   ✅ User notification sent")
        except Exception as e:
            print(f"   ⚠️ Failed to send user notification: {str(e)}")
            import traceback
            traceback.print_exc()
        
        return format_success_response({
            'post': post.to_dict(),
            'old_status': old_status,
            'new_status': new_status
        }, 'Status updated successfully')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to update status: {str(e)}', 500)


@posts_bp.route('/<int:post_id>/reply', methods=['POST'])
def add_officer_reply(post_id):
    """Officer submits a reply/report to a post"""
    try:
        from location_service import notify_officer_reply
        
        data = request.get_json()
        
        if not data.get('officer_name') or not data.get('message'):
            return format_error_response('officer_name and message are required')
        
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
        # Create officer reply
        reply = OfficerReply(
            post_id=post_id,
            officer_name=data['officer_name'],
            message=data['message']
        )
        
        db.session.add(reply)
        db.session.commit()
        
        # Notify user about the reply
        notify_officer_reply(post, data['officer_name'])
        
        print(f"✅ Officer {data['officer_name']} replied to post {post_id}")
        
        return format_success_response({
            'reply': reply.to_dict(),
            'post': post.to_dict()
        }, 'Reply added successfully')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to add reply: {str(e)}', 500)


@posts_bp.route('/<int:post_id>/replies', methods=['GET'])
def get_post_replies(post_id):
    """Get all replies for a post"""
    try:
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
        replies = OfficerReply.query.filter_by(post_id=post_id).order_by(OfficerReply.created_at.desc()).all()
        
        return format_success_response({
            'replies': [reply.to_dict() for reply in replies],
            'count': len(replies)
        }, 'Replies retrieved successfully')
    
    except Exception as e:
        return format_error_response(f'Failed to get replies: {str(e)}', 500)


@posts_bp.route('/dashboard/stats/<int:officer_id>', methods=['GET'])
def get_dashboard_stats(officer_id):
    """Get dashboard statistics for an officer"""
    try:
        from location_service import get_officer_stats
        
        stats = get_officer_stats(officer_id)
        
        # Get recent posts
        recent_posts = Post.query.filter_by(assigned_officer_id=officer_id)\
            .order_by(Post.created_at.desc())\
            .limit(6)\
            .all()
        
        return format_success_response({
            'stats': stats,
            'recent_posts': [post.to_dict() for post in recent_posts]
        }, 'Dashboard stats retrieved successfully')
    
    except Exception as e:
        return format_error_response(f'Failed to get dashboard stats: {str(e)}', 500)
