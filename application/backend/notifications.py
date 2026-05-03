from flask import Blueprint, request, jsonify
from models import db, Notification, Post, User
from utils import format_error_response, format_success_response

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


def create_notification(user_id, title, message, notification_type='info', post_id=None, action_url=None):
    """
    Helper function to create a notification
    
    Args:
        user_id: ID of the user to notify
        title: Notification title
        message: Notification message
        notification_type: Type of notification (info, status_update, completion_verification, etc.)
        post_id: Optional post ID
        action_url: Optional deep link URL
    
    Returns:
        Created notification object or None if failed
    """
    try:
        notification = Notification(
            user_id=user_id,
            post_id=post_id,
            title=title,
            message=message,
            type=notification_type,
            action_url=action_url
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        db.session.rollback()
        print(f"Error creating notification: {str(e)}")
        return None


def notify_user_status_change(post, new_status):
    """Notify user when officer changes issue status"""
    # Truncate description to 50 characters for notification
    desc = post.description[:50] + '...' if len(post.description) > 50 else post.description
    
    status_messages = {
        'seen': f'Your post "{desc}" has been seen by an officer',
        'verified': f'Your post "{desc}" has been verified',
        'hold': f'Your post "{desc}" has been put on hold',
        'in_progress': f'Work has started on your post "{desc}"',
        'completed': f'Your post "{desc}" has been marked as completed. Please verify!',
        'closed': f'Your post "{desc}" has been successfully resolved and closed'
    }
    
    message = status_messages.get(new_status, f'Your post "{desc}" status changed to {new_status}')
    notif_type = 'completion_verification' if new_status == 'completed' else 'status_update'
    
    print(f"\n📧 Creating user notification:")
    print(f"   Post ID: {post.id}")
    print(f"   New Status: {new_status}")
    print(f"   Notification Type: {notif_type}")
    print(f"   Message: {message}")
    
    notification = create_notification(
        user_id=post.user_id,
        title='Issue Status Updated',
        message=message,
        notification_type=notif_type,
        post_id=post.id,
        action_url=f'/my-requests/{post.id}'
    )
    
    if notification:
        print(f"   ✅ Notification created (ID: {notification.id}, Type: {notification.type})")
    else:
        print(f"   ❌ Failed to create notification")
    
    return notification


def notify_officer_new_issue(post, officer_id):
    """Notify officer when new issue is assigned (DEPRECATED - use notify_all_region_officers_new_post)"""
    return create_notification(
        user_id=officer_id,
        title='New Issue Received',
        message=f'New {post.issue_type} issue: {post.description[:50]}...',
        notification_type='info',
        post_id=post.id,
        action_url=f'/issue/{post.id}'
    )


def notify_all_region_officers_new_post(post):
    """
    Notify ALL officers in the region about a new post
    This ensures all officers in the same region see new posts immediately
    
    Args:
        post: Post object with province, district, region fields
    
    Returns:
        Number of notifications created
    """
    try:
        print(f"\n{'='*80}")
        print(f"🔔 NOTIFYING OFFICERS - New Post {post.id}")
        print(f"{'='*80}")
        print(f"Post Details:")
        print(f"  - Region: {post.region}")
        print(f"  - District: {post.district}")
        print(f"  - Province: {post.province}")
        print(f"  - Issue Type: {post.issue_type}")
        print(f"  - Location: {post.location}")
        
        # Get all officers for this region AND matching issue type
        # CRITICAL: Filter by officer_type to match post's issue_type
        # NOTE: officer_type is lowercase ('road', 'garbage') but issue_type is capitalized ('Road', 'Garbage')
        officer_type_filter = post.issue_type.lower() if post.issue_type else None
        
        officers_query = User.query.filter_by(
            is_officer=True,
            officer_province=post.province,
            officer_district=post.district,
            officer_region=post.region
        )
        
        if officer_type_filter:
            officers_query = officers_query.filter_by(officer_type=officer_type_filter)
        
        officers = officers_query.all()
        
        print(f"\nOfficers Query:")
        print(f"  - Searching for officers in: {post.region}, {post.district}, {post.province}")
        print(f"  - Officer Type Filter: {officer_type_filter}")
        print(f"  - Officers found: {len(officers)}")
        
        if not officers:
            print(f"⚠️  WARNING: No officers found for region!")
            print(f"   Please create officers for: {post.region}, {post.district}, {post.province}")
            return 0
        
        print(f"\nCreating notifications for {len(officers)} officers:")
        notifications_created = 0
        for officer in officers:
            print(f"  - Notifying: {officer.username} (ID: {officer.id})")
            notification = create_notification(
                user_id=officer.id,
                title=f'New {post.issue_type} Issue in Your Region',
                message=f'New issue at {post.location}: {post.description[:50]}...',
                notification_type='new_post',
                post_id=post.id,
                action_url=f'/issue/{post.id}'
            )
            if notification:
                notifications_created += 1
                print(f"    ✅ Notification created (ID: {notification.id})")
            else:
                print(f"    ❌ Failed to create notification")
        
        print(f"\n✅ SUCCESS: Notified {notifications_created}/{len(officers)} officers")
        print(f"{'='*80}\n")
        return notifications_created
        
    except Exception as e:
        print(f"\n❌ ERROR in notify_all_region_officers_new_post: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0


def notify_region_officers_status_change(post, new_status, changing_officer_id=None):
    """
    Notify ALL other officers in the region when status changes
    This keeps all officers informed about post updates made by their peers
    
    Args:
        post: Post object with province, district, region fields
        new_status: New status value
        changing_officer_id: ID of officer who made the change (optional)
    
    Returns:
        Number of notifications created
    """
    try:
        # Get all officers for this region AND matching issue type
        officer_type_filter = post.issue_type.lower() if post.issue_type else None
        
        officers_query = User.query.filter_by(
            is_officer=True,
            officer_province=post.province,
            officer_district=post.district,
            officer_region=post.region
        )
        
        if officer_type_filter:
            officers_query = officers_query.filter_by(officer_type=officer_type_filter)
        
        officers = officers_query.all()
        
        if not officers:
            return 0
        
        # Get the officer who made the change
        officer_name = "An officer"
        if changing_officer_id:
            changing_officer = User.query.get(changing_officer_id)
            if changing_officer:
                officer_name = changing_officer.username
        
        notifications_created = 0
        for officer in officers:
            # Skip the officer who made the change
            if changing_officer_id and officer.id == changing_officer_id:
                continue
            
            notification = create_notification(
                user_id=officer.id,
                title=f'Status Updated by {officer_name}',
                message=f'{officer_name} changed post status to: {new_status}',
                notification_type='status_update',
                post_id=post.id,
                action_url=f'/issue/{post.id}'
            )
            if notification:
                notifications_created += 1
        
        if notifications_created > 0:
            print(f"✅ Notified {notifications_created} officers about status change to {new_status}")
        return notifications_created
        
    except Exception as e:
        print(f"❌ Error notifying region officers about status change: {str(e)}")
        return 0


def notify_officer_user_verification(post, verified):
    """Notify officer when user verifies/rejects completion"""
    if verified:
        title = 'User Verified Completion'
        message = 'User confirmed the issue is fixed. You can now close it.'
        notif_type = 'user_verified'
    else:
        title = 'User Rejected Completion'
        message = 'User says the issue is not fixed. Please review.'
        notif_type = 'user_rejected'
    
    return create_notification(
        user_id=post.assigned_officer_id,
        title=title,
        message=message,
        notification_type=notif_type,
        post_id=post.id,
        action_url=f'/issue/{post.id}'
    )


@notifications_bp.route('/<int:user_id>', methods=['GET'])
def get_user_notifications(user_id):
    """Get all notifications for a user"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        # Query notifications
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Convert to dict
        notifications_data = []
        for notification in notifications.items:
            notif_dict = notification.to_dict()
            
            # Include post title if available
            if notification.post_id:
                post = Post.query.get(notification.post_id)
                if post:
                    notif_dict['post_title'] = post.title
            
            notifications_data.append(notif_dict)
        
        return format_success_response({
            'notifications': notifications_data,
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': notifications.page
        })
    
    except Exception as e:
        return format_error_response(f'Failed to get notifications: {str(e)}', 500)


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
def mark_as_read(notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            return format_error_response('Notification not found', 404)
        
        notification.read = True
        db.session.commit()
        
        return format_success_response(
            notification.to_dict(),
            'Notification marked as read'
        )
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to mark notification as read: {str(e)}', 500)


@notifications_bp.route('/unread-count/<int:user_id>', methods=['GET'])
def get_unread_count(user_id):
    """Get count of unread notifications for a user"""
    try:
        count = Notification.query.filter_by(user_id=user_id, read=False).count()
        
        return format_success_response({
            'user_id': user_id,
            'unread_count': count
        })
    
    except Exception as e:
        return format_error_response(f'Failed to get unread count: {str(e)}', 500)


@notifications_bp.route('/mark-all-read/<int:user_id>', methods=['PUT'])
def mark_all_as_read(user_id):
    """Mark all notifications as read for a user"""
    try:
        Notification.query.filter_by(user_id=user_id, read=False).update({'read': True})
        db.session.commit()
        
        return format_success_response(
            {'user_id': user_id},
            'All notifications marked as read'
        )
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to mark all as read: {str(e)}', 500)


@notifications_bp.route('/verify-completion/<int:post_id>', methods=['POST'])
def verify_completion(post_id):
    """User verifies or rejects issue completion"""
    try:
        from models import Achievement
        from datetime import datetime
        
        data = request.get_json()
        verified = data.get('verified', False)
        user_id = data.get('user_id')
        
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
        # Check if user owns this post
        if post.user_id != user_id:
            return format_error_response('Unauthorized', 403)
        
        # Update post
        post.user_verified_completion = verified
        
        if verified:
            # User accepted - AUTO-CLOSE and CREATE ACHIEVEMENT
            print(f"\n✅ User verified completion for post {post_id}")
            
            # 1. Change status to CLOSED
            post.status = 'closed'
            post.closed_at = datetime.utcnow()
            print(f"   Status changed to: closed")
            
            # 2. Create Achievement automatically
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
                    print(f"   ✅ Achievement created for post {post_id}")
                    
                    # 3. Notify ALL officers in region about new achievement
                    try:
                        officer_type_filter = post.issue_type.lower() if post.issue_type else None
                        
                        officers_query = User.query.filter_by(
                            is_officer=True,
                            officer_province=post.province,
                            officer_district=post.district,
                            officer_region=post.region
                        )
                        
                        if officer_type_filter:
                            officers_query = officers_query.filter_by(officer_type=officer_type_filter)
                        
                        officers = officers_query.all()
                        
                        for officer in officers:
                            create_notification(
                                user_id=officer.id,
                                title='New Achievement in Your Region',
                                message=f'Issue "{post.description[:50]}..." has been successfully resolved!',
                                notification_type='achievement',
                                post_id=post.id,
                                action_url=f'/achievements'
                            )
                        print(f"   ✅ Notified {len(officers)} officers about new achievement")
                    except Exception as e:
                        print(f"   ⚠️  Failed to notify officers about achievement: {str(e)}")
                else:
                    print(f"   ℹ️  Achievement already exists for post {post_id}")
            except Exception as e:
                print(f"   ⚠️  Failed to create achievement: {str(e)}")
            
            # 4. Notify assigned officer user verified
            notify_officer_user_verification(post, True)
            print(f"   Assigned officer notified of user verification")
            
        else:
            # User rejected - notify officer to review
            print(f"\n❌ User rejected completion for post {post_id}")
            notify_officer_user_verification(post, False)
            # Revert status back to in_progress
            post.status = 'in_progress'
            print(f"   Status reverted to: in_progress")
        
        db.session.commit()
        
        return format_success_response(
            post.to_dict(),
            'Verification recorded successfully'
        )
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in verify_completion: {str(e)}")
        import traceback
        traceback.print_exc()
        return format_error_response(f'Failed to verify completion: {str(e)}', 500)


@notifications_bp.route('/achievements', methods=['GET'])
def get_achievements():
    """Get achievements filtered by officer region if officer_id provided"""
    try:
        from models import Achievement, Post, User
        
        # Get officer_id from query params
        officer_id = request.args.get('officer_id', type=int)
        
        if officer_id:
            # Get officer details
            officer = User.query.get(officer_id)
            if officer and officer.is_officer:
                # Filter achievements by officer's region AND type
                achievements_query = Achievement.query.join(Post).filter(
                    Post.province == officer.officer_province,
                    Post.district == officer.officer_district,
                    Post.region == officer.officer_region
                )
                
                # CRITICAL: Also filter by officer type (Road/Garbage)
                if officer.officer_type:
                    issue_type_filter = officer.officer_type.capitalize()
                    achievements_query = achievements_query.filter(Post.issue_type == issue_type_filter)
                
                achievements = achievements_query.order_by(Achievement.completed_date.desc()).all()
            else:
                achievements = Achievement.query.order_by(Achievement.completed_date.desc()).all()
        else:
            # No officer_id - return all achievements
            achievements = Achievement.query.order_by(Achievement.completed_date.desc()).all()
        
        return format_success_response({
            'achievements': [achievement.to_dict() for achievement in achievements],
            'total': len(achievements)
        })
    
    except Exception as e:
        return format_error_response(f'Failed to get achievements: {str(e)}', 500)


@notifications_bp.route('/achievements/officer/<int:officer_id>', methods=['GET'])
def get_officer_achievements(officer_id):
    """Get achievements for a specific officer"""
    try:
        from models import Achievement
        
        achievements = Achievement.query.filter_by(officer_id=officer_id).order_by(
            Achievement.completed_date.desc()
        ).all()
        
        return format_success_response({
            'achievements': [achievement.to_dict() for achievement in achievements],
            'total': len(achievements),
            'officer_id': officer_id
        })
    
    except Exception as e:
        return format_error_response(f'Failed to get officer achievements: {str(e)}', 500)


def notify_officers_repost(post, comment):
    """
    Notify all officers in the region when user creates a repost (comment with image)
    
    Args:
        post (Post): The original post
        comment (Comment): The comment/repost created by user
    
    Returns:
        Number of notifications created
    """
    try:
        print(f"\n🔔 NOTIFYING OFFICERS - User Repost on Post {post.id}")
        print(f"   Post Region Data:")
        print(f"     - Province: '{post.province}'")
        print(f"     - District: '{post.district}'")
        print(f"     - Region: '{post.region}'")
        print(f"     - Issue Type: '{post.issue_type}'")
        
        # Get all officers for this region AND matching issue type
        # CRITICAL: Filter by officer_type to match post's issue_type
        # NOTE: officer_type is lowercase ('road', 'garbage') but issue_type is capitalized ('Road', 'Garbage')
        officers_query = User.query.filter_by(
            is_officer=True,
            officer_province=post.province,
            officer_district=post.district,
            officer_region=post.region
        )
        
        # Filter by officer type matching post's issue type
        if post.issue_type:
            # Convert issue_type to lowercase to match officer_type
            officer_type_filter = post.issue_type.lower()  # 'Road' → 'road'
            officers_query = officers_query.filter_by(officer_type=officer_type_filter)
            print(f"   🔍 Filtering officers by type: {officer_type_filter} (from issue_type: {post.issue_type})")
        
        officers = officers_query.all()
        
        print(f"   Officers found: {len(officers)}")
        
        if not officers:
            print(f"   ⚠️  No officers found for region!")
            print(f"   Searching for officers with:")
            print(f"     - officer_province = '{post.province}'")
            print(f"     - officer_district = '{post.district}'")
            print(f"     - officer_region = '{post.region}'")
            
            # Debug: Show all officers in database
            all_officers = User.query.filter_by(is_officer=True).all()
            print(f"\n   📋 All officers in database ({len(all_officers)}):")
            for off in all_officers:
                print(f"     - {off.username}: {off.officer_region}, {off.officer_district}, {off.officer_province}")
            return 0
        
        # Get user's display name
        user = User.query.get(comment.user_id)
        user_name = user.display_name if user and user.display_name else 'User'
        
        notifications_created = 0
        for officer in officers:
            notification = create_notification(
                user_id=officer.id,
                title=f'User Update on Issue',
                message=f'{user_name} added an update with image to their post at {post.location}',
                notification_type='repost',
                post_id=post.id,
                action_url=f'/issue/{post.id}'
            )
            if notification:
                notifications_created += 1
        
        print(f"   ✅ Notified {notifications_created}/{len(officers)} officers about repost")
        return notifications_created
        
    except Exception as e:
        print(f"   ❌ Error notifying officers about repost: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0
