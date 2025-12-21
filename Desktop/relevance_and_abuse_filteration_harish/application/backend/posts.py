from flask import Blueprint, request, jsonify
from models import db, Post, ComponentResult, Notification, OfficerReply, User, Achievement
from utils import format_error_response, format_success_response, save_image, get_image_base64
from components import process_components_parallel
from config import Config
from datetime import datetime
import os
import base64

posts_bp = Blueprint('posts', __name__, url_prefix='/api/posts')


@posts_bp.route('', methods=['GET'])
def get_all_posts():
    """Get all approved posts (for app dashboard)"""
    try:
        limit = request.args.get('limit', type=int, default=20)
        offset = request.args.get('offset', type=int, default=0)
        
        # Get all submitted/approved posts (not rejected or processing)
        posts = Post.query.filter(
            Post.status.in_(['submitted', 'seen', 'verified', 'hold', 'in_progress', 'completed'])
        ).order_by(Post.created_at.desc()).limit(limit).offset(offset).all()
        
        posts_data = []
        for post in posts:
            post_dict = post.to_dict()
            
            # Convert image filenames to base64
            images_base64 = []
            for img_filename in post.get_images():
                img_base64 = get_image_base64(img_filename)
                if img_base64:
                    images_base64.append(img_base64)
            post_dict['images'] = images_base64
            
            posts_data.append(post_dict)
        
        return format_success_response({
            'posts': posts_data,
            'count': len(posts_data)
        })
    
    except Exception as e:
        return format_error_response(f'Failed to get posts: {str(e)}', 500)


@posts_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_posts(user_id):
    """Get posts by a specific user (for My Requests page)"""
    try:
        limit = request.args.get('limit', type=int, default=20)
        offset = request.args.get('offset', type=int, default=0)
        
        posts = Post.query.filter_by(user_id=user_id)\
            .order_by(Post.created_at.desc())\
            .limit(limit).offset(offset).all()
        
        posts_data = []
        for post in posts:
            post_dict = post.to_dict()
            
            # Convert image filenames to base64
            images_base64 = []
            for img_filename in post.get_images():
                img_base64 = get_image_base64(img_filename)
                if img_base64:
                    images_base64.append(img_base64)
            post_dict['images'] = images_base64
            
            # Include officer replies
            replies = [reply.to_dict() for reply in post.officer_replies]
            post_dict['officer_replies'] = replies
            
            posts_data.append(post_dict)
        
        return format_success_response({
            'posts': posts_data,
            'count': len(posts_data)
        })
    
    except Exception as e:
        return format_error_response(f'Failed to get user posts: {str(e)}', 500)


@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get a single post by ID"""
    try:
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
        post_dict = post.to_dict()
        
        # Convert image filenames to base64
        images_base64 = []
        for img_filename in post.get_images():
            img_base64 = get_image_base64(img_filename)
            if img_base64:
                images_base64.append(img_base64)
        post_dict['images'] = images_base64
        
        # Include officer replies
        replies = [reply.to_dict() for reply in post.officer_replies]
        post_dict['officer_replies'] = replies
        
        return format_success_response(post_dict)
    
    except Exception as e:
        return format_error_response(f'Failed to get post: {str(e)}', 500)


@posts_bp.route('/submit', methods=['POST'])
def submit_post():
    """Submit a new post with component processing and GPS-based officer routing"""
    try:
        from location_service import assign_officer_to_post
        
        data = request.get_json()
        
        # Get user_id from request data (sent by mobile app)
        current_user_id = data.get('user_id')
        if not current_user_id:
            return format_error_response('user_id is required')
        
        # Validate required fields
        required_fields = ['title', 'description', 'location', 'issue_type']
        for field in required_fields:
            if not data.get(field):
                return format_error_response(f'Missing required field: {field}')
        
        # Validate images
        if not data.get('images') or len(data['images']) == 0:
            return format_error_response('At least one image is required')
        
        # Create post with GPS coordinates and location data
        new_post = Post(
            user_id=current_user_id,
            title=data['title'],
            description=data['description'],
            location=data['location'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            province=data.get('province'),
            district=data.get('district'),
            region=data.get('region'),  # ✅ ADDED - Accept region from mobile app
            issue_type=data['issue_type'],
            road_type=data.get('road_type'),  # Road issue type (only for Road issues)
            priority=data.get('priority', 'medium'),
            status='processing'
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        # Assign officer based on GPS location
        assigned_officer = assign_officer_to_post(new_post)
        if assigned_officer:
            print(f"✅ Assigned to officer: {assigned_officer.username} ({assigned_officer.officer_title})")
        else:
            print(f"⚠️  No officer found for: {new_post.province}, {new_post.district}")
        db.session.commit()
        
        # Save images
        print(f"📸 Saving images for post {new_post.id}...")
        print(f"   Images received: {len(data.get('images', []))} images")
        
        saved_images = []
        for idx, image_data in enumerate(data['images']):
            filename = f"post_{new_post.id}_img_{idx}.jpg"
            print(f"   Saving image {idx}: {filename}")
            saved_filename = save_image(image_data, filename)
            if saved_filename:
                print(f"   ✅ Saved as: {saved_filename}")
                saved_images.append(saved_filename)
            else:
                print(f"   ❌ Failed to save image {idx}")
        
        print(f"   Total saved: {len(saved_images)} images")
        print(f"   Saved filenames: {saved_images}")
        
        new_post.set_images(saved_images)
        print(f"   Post images field set to: {new_post.images}")
        db.session.commit()
        print(f"   ✅ Database committed")
        
        # Process components in parallel
        print(f"🔄 Processing post {new_post.id} through 4 components...")
        
        # Get first image for component processing
        first_image = data['images'][0] if data['images'] else ''
        
        component_results = process_components_parallel(
            image_data=first_image,
            description=data['description'],
            timeout=60
        )
        
        # Save component results
        new_post.set_component_results(component_results['results'])
        
        # Save individual component results
        for component_name, component_data in component_results['results'].items():
            result_record = ComponentResult(
                post_id=new_post.id,
                component_name=component_name,
                status=component_data['result']['status'],
                processing_time=component_data['processing_time']
            )
            result_record.set_result_data(component_data['result'])
            db.session.add(result_record)
        
        
        # Update post status based on component results
        if component_results['all_passed']:
            new_post.status = 'submitted'  # Changed from 'approved' to 'submitted'
            new_post.rejection_reason = None
            
            # Create notification for user
            desc = new_post.description[:50] + '...' if len(new_post.description) > 50 else new_post.description
            notification = Notification(
                user_id=current_user_id,
                post_id=new_post.id,
                title='Issue Posted Successfully',
                message=f'Your post "{desc}" has been submitted and assigned to an officer.',
                type='info',
                action_url=f'/my-requests/{new_post.id}'
            )
            db.session.add(notification)

            
            print(f"✅ Post {new_post.id} APPROVED - All components passed")
        else:
            new_post.status = 'rejected'
            new_post.rejection_reason = component_results['summary']
            
            # Create notification for user
            desc = new_post.description[:50] + '...' if len(new_post.description) > 50 else new_post.description
            notification = Notification(
                user_id=current_user_id,
                post_id=new_post.id,
                title='Post Rejected',
                message=f'Your post "{desc}" was rejected. Reason: {component_results["summary"]}',
                type='status_update'
            )
            db.session.add(notification)

            
            print(f"❌ Post {new_post.id} REJECTED - {component_results['summary']}")
        
        # Commit the post and user notifications
        db.session.commit()

        # 🔔 CRITICAL: Notify officers for ALL posts (approved AND rejected)
        # Like social media, officers should see ALL posts in their region
        if new_post.province and new_post.district and new_post.region:
            print(f"\n🔔 Triggering officer notifications for post {new_post.id}...")
            try:
                from notifications import notify_all_region_officers_new_post
                officers_notified = notify_all_region_officers_new_post(new_post)
                print(f"✅ Officer notification complete: {officers_notified} officers notified")
            except Exception as e:
                print(f"❌ Failed to notify region officers: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"⚠️  Cannot notify officers - missing region data:")
            print(f"   Province: {new_post.province}")
            print(f"   District: {new_post.district}")
            print(f"   Region: {new_post.region}")
        
        return format_success_response({
            'post': new_post.to_dict(),
            'component_results': component_results,
            'processing_time': component_results['total_time']
        }, f'Post {new_post.status}')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to submit post: {str(e)}', 500)


# ===== OFFICER-SPECIFIC ENDPOINTS =====

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
        # This shows ALL posts in the officer's region, not just assigned to them
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
        
        # Convert to dict with images as base64
        posts_data = []
        for post in posts:
            post_dict = post.to_dict()
            
            # Add images as base64
            images = post.get_images()
            post_dict['images'] = []
            for img_filename in images:
                img_path = os.path.join(Config.UPLOAD_FOLDER, img_filename)
                if os.path.exists(img_path):
                    with open(img_path, 'rb') as img_file:
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        # Add data URI prefix for browser display
                        post_dict['images'].append(f'data:image/jpeg;base64,{img_data}')
            
            posts_data.append(post_dict)
        
        # Get officer stats
        stats = get_officer_stats(officer_id)
        
        return format_success_response({
            'posts': posts_data,
            'total_count': total_count,
            'stats': stats,
            'limit': limit,
            'offset': offset
        }, 'Posts retrieved successfully')
    
    except Exception as e:
        return format_error_response(f'Failed to get officer posts: {str(e)}', 500)


@posts_bp.route('/<int:post_id>/status', methods=['PUT'])
def update_post_status(post_id):
    """Update post status and notify user - FIXED VERSION"""
    print(f"\n🚀 UPDATE_POST_STATUS CALLED - Post ID: {post_id}")
    try:
        from notifications import notify_user_status_change, notify_region_officers_status_change
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
        
        return format_success_response({
            'post': post.to_dict(),
            'old_status': old_status,
            'new_status': new_status
        }, 'Status updated successfully')
    
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR in update_post_status:")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
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
        # Website sends 'images' as array, extract first image if present
        image_data = None
        if data.get('images') and len(data['images']) > 0:
            image_data = data['images'][0]
        elif data.get('image'):
            image_data = data['image']
            
        reply = OfficerReply(
            post_id=post_id,
            officer_name=data['officer_name'],
            message=data['message'],
            image=image_data  # Include image if provided
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
        
        # Convert to dict with images as base64
        posts_data = []
        for post in recent_posts:
            post_dict = post.to_dict()
            
            # Convert image filenames to base64
            images_base64 = []
            for img_filename in post.get_images():
                img_base64 = get_image_base64(img_filename)
                if img_base64:
                    images_base64.append(img_base64)
            post_dict['images'] = images_base64
            
            posts_data.append(post_dict)
        
        return format_success_response({
            'stats': stats,
            'recent_posts': posts_data
        }, 'Dashboard stats retrieved successfully')
    
    except Exception as e:
        return format_error_response(f'Failed to get dashboard stats: {str(e)}', 500)


@posts_bp.route('/<int:post_id>/status', methods=['GET'])
def get_post_status(post_id):
    """Get post processing status and component results"""
    try:
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
        # Get component results
        component_results = ComponentResult.query.filter_by(post_id=post_id).all()
        
        return format_success_response({
            'post_id': post_id,
            'status': post.status,
            'component_results': [result.to_dict() for result in component_results],
            'rejection_reason': post.rejection_reason
        })
    
    except Exception as e:
        return format_error_response(f'Failed to get post status: {str(e)}', 500)