from flask import Blueprint, request, jsonify
from models import db, Post, Like, Comment, Share, User
from utils import format_error_response, format_success_response

interactions_bp = Blueprint('interactions', __name__, url_prefix='/api/interactions')

# ==================== LIKE ENDPOINTS ====================

@interactions_bp.route('/like/<int:post_id>', methods=['POST'])
def toggle_like(post_id):
    """Toggle like on a post"""
    try:
        # Get user_id from request body
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return format_error_response('user_id is required', 400)
        
        # Check if post exists
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
        # Check if user already liked this post
        existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        
        if existing_like:
            # Unlike
            db.session.delete(existing_like)
            db.session.commit()
            
            return format_success_response({
                'liked': False,
                'like_count': len(post.likes)
            }, 'Post unliked')
        else:
            # Like
            new_like = Like(post_id=post_id, user_id=user_id)
            db.session.add(new_like)
            db.session.commit()
            
            return format_success_response({
                'liked': True,
                'like_count': len(post.likes)
            }, 'Post liked')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to toggle like: {str(e)}', 500)


@interactions_bp.route('/check-like/<int:post_id>', methods=['POST'])
def check_like(post_id):
    """Check if user has liked a post"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return format_error_response('user_id is required', 400)
        
        existing_like = Like.query.filter_by(post_id=post_id, user_id=user_id).first()
        
        return format_success_response({
            'liked': existing_like is not None
        })
    
    except Exception as e:
        return format_error_response(f'Failed to check like: {str(e)}', 500)


# ==================== COMMENT ENDPOINTS ====================

@interactions_bp.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    """Add a comment to a post"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return format_error_response('user_id is required', 400)
        
        if not data.get('text'):
            return format_error_response('Comment text is required', 400)
        
        # Check if post exists
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
        # Check if this is a repost (original author + has image)
        # Convert user_id to int for comparison (mobile app sends as string)
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            user_id_int = user_id
        
        is_original_author = (user_id_int == post.user_id)
        has_image = data.get('image') is not None and data.get('image') != ''
        is_repost = is_original_author and has_image
        
        print(f"\n🔍 REPOST CHECK:")
        print(f"   User ID (from app): {user_id} (type: {type(user_id)})")
        print(f"   User ID (converted): {user_id_int} (type: {type(user_id_int)})")
        print(f"   Post User ID: {post.user_id} (type: {type(post.user_id)})")
        print(f"   Is Original Author: {is_original_author}")
        print(f"   Has Image: {has_image}")
        print(f"   Is Repost: {is_repost}")
        
        # Create comment
        new_comment = Comment(
            post_id=post_id,
            user_id=user_id,
            text=data['text'],
            image=data.get('image'),  # Include image if provided
            is_repost=is_repost  # Flag as repost if original author with image
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        # If this is a reply from the author (repost or just text reply), notify officers
        if is_original_author:
            try:
                # We reuse the repost notification function but update the message logic inside it
                # or just create a new notification here.
                # Let's call a notification function that handles both.
                
                # Get user's display name for notification
                user = User.query.get(user_id)
                # Use display_name if available (anonymous), otherwise username
                notify_name = user.display_name if user.display_name else user.username
                
                # Determine notification title and message based on content
                notif_title = 'User Update on Issue'
                if has_image:
                    notif_msg = f'{notify_name} added an update with image to their post at {post.location}'
                else:
                    notif_msg = f'{notify_name} commented on their post: {data["text"][:50]}...'
                
                # Get officers in region AND matching issue type
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
                
                from notifications import create_notification
                notified_count = 0
                for officer in officers:
                    create_notification(
                        user_id=officer.id,
                        title=notif_title,
                        message=notif_msg,
                        notification_type='repost' if has_image else 'comment',
                        post_id=post.id,
                        action_url=f'/issue/{post.id}'
                    )
                    notified_count += 1
                
                print(f"✅ Notified {notified_count} officers about user reply (simulated repost)")

            except Exception as e:
                print(f"⚠️ Failed to notify officers about user reply: {str(e)}")
        
        return format_success_response({
            'comment': new_comment.to_dict(),
            'comment_count': len(post.comments) + len(post.officer_replies),
            'is_repost': is_repost
        }, 'Comment added')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to add comment: {str(e)}', 500)


@interactions_bp.route('/comments/<int:post_id>', methods=['GET'])
def get_comments(post_id):
    """Get all comments for a post, including officer replies"""
    try:
        from models import OfficerReply, User
        
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
        # Get regular comments
        comments = Comment.query.filter_by(post_id=post_id).all()
        
        # Get officer replies
        officer_replies = OfficerReply.query.filter_by(post_id=post_id).all()
        
        # Merge comments and officer replies
        all_comments = []
        
        # Add regular comments
        for comment in comments:
            comment_dict = comment.to_dict()
            comment_dict['is_officer'] = False
            
            # Add user details
            # Fetch user to get name (handle anonymous display name)
            user = User.query.get(comment.user_id)
            if user:
                # Logic: If user has display_name set, use it. Otherwise username.
                # This ensures anonymous users (who have display_name set) show as "Albert" etc.
                comment_dict['username'] = user.display_name if user.display_name else user.username
                comment_dict['avatar_type'] = user.avatar_type
            else:
                comment_dict['username'] = 'Unknown User'
            
            all_comments.append(comment_dict)
        
        # Add officer replies as comments
        for reply in officer_replies:
            all_comments.append({
                'id': f'officer_{reply.id}',  # Prefix to avoid ID conflicts
                'post_id': reply.post_id,
                'username': reply.officer_name,
                'text': reply.message,
                'image': reply.image,  # Include officer reply image
                'created_at': reply.created_at.isoformat(),
                'is_officer': True,  # Mark as officer comment
                'officer_name': reply.officer_name
            })
        
        # Sort by created_at descending (newest first)
        all_comments.sort(key=lambda x: x['created_at'], reverse=True)
        
        return format_success_response({
            'comments': all_comments,
            'total': len(all_comments)
        })
    
    except Exception as e:
        return format_error_response(f'Failed to get comments: {str(e)}', 500)



# ==================== SHARE ENDPOINTS ====================

@interactions_bp.route('/share/<int:post_id>', methods=['POST'])
def share_post(post_id):
    """Share a post (track share count)"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id')
        
        if not user_id:
            return format_error_response('user_id is required', 400)
        
        # Check if post exists
        post = Post.query.get(post_id)
        if not post:
            return format_error_response('Post not found', 404)
        
        # Create share record
        new_share = Share(post_id=post_id, user_id=user_id)
        db.session.add(new_share)
        db.session.commit()
        
        return format_success_response({
            'share_count': len(post.shares)
        }, 'Post shared')
    
    except Exception as e:
        db.session.rollback()
        return format_error_response(f'Failed to share post: {str(e)}', 500)


@interactions_bp.route('/reposted-posts/<int:officer_id>', methods=['GET'])
def get_reposted_posts(officer_id):
    """Get posts with user reposts OR officer replies with images for officer dashboard 'Reposted Posts' section"""
    try:
        from models import User, Comment, OfficerReply
        
        # Get officer details
        officer = User.query.get(officer_id)
        if not officer or not officer.is_officer:
            return format_error_response('Officer not found', 404)
        
        # Get posts in officer's region that have EITHER:
        # 1. User reposts (is_repost = True) - original author with image
        # 2. Officer replies with images
        
        # Get posts in officer's region that have:
        # 1. User replies (author comments) - whether text or image
        # 2. Officer replies with images
        
        # CRITICAL: Filter by officer type (Road/Garbage)
        # NOTE: officer_type is lowercase ('road', 'garbage') but issue_type is capitalized ('Road', 'Garbage')
        issue_type_filter = None
        if officer.officer_type:
            issue_type_filter = officer.officer_type.capitalize()
            print(f"📊 Reposted posts filtered for Officer {officer.username} (Type: {officer.officer_type} -> {issue_type_filter})")
        
        # Get posts with user replies (author comments) - Relaxed from is_repost=True to any author comment
        posts_with_user_replies_query = db.session.query(Post).join(Comment).filter(
            Post.province == officer.officer_province,
            Post.district == officer.officer_district,
            Post.region == officer.officer_region,
            Comment.user_id == Post.user_id  # Any comment by the author
        )
        if issue_type_filter:
            posts_with_user_replies_query = posts_with_user_replies_query.filter(Post.issue_type == issue_type_filter)
        posts_with_user_replies = posts_with_user_replies_query.distinct().all()
        
        # Get posts with officer replies that have images
        posts_with_officer_images_query = db.session.query(Post).join(OfficerReply).filter(
            Post.province == officer.officer_province,
            Post.district == officer.officer_district,
            Post.region == officer.officer_region,
            OfficerReply.image.isnot(None),
            OfficerReply.image != ''
        )
        if issue_type_filter:
            posts_with_officer_images_query = posts_with_officer_images_query.filter(Post.issue_type == issue_type_filter)
        posts_with_officer_images = posts_with_officer_images_query.distinct().all()
        
        # Combine and deduplicate posts
        all_posts = {post.id: post for post in posts_with_user_replies}
        for post in posts_with_officer_images:
            all_posts[post.id] = post
        
        # Sort by updated_at descending
        sorted_posts = sorted(all_posts.values(), key=lambda p: p.updated_at, reverse=True)
        
        posts_data = []
        for post in sorted_posts:
            post_dict = post.to_dict()
            
            # Get user comments for this post (filter for author comments)
            user_reposts = Comment.query.filter_by(
                post_id=post.id
            ).filter(Comment.user_id == post.user_id).order_by(Comment.created_at.desc()).all()
            
            # Get officer replies with images for this post
            officer_replies_with_images = OfficerReply.query.filter(
                OfficerReply.post_id == post.id,
                OfficerReply.image.isnot(None),
                OfficerReply.image != ''
            ).order_by(OfficerReply.created_at.desc()).all()
            
            post_dict['user_reposts'] = [repost.to_dict() for repost in user_reposts]
            post_dict['officer_replies_with_images'] = [reply.to_dict() for reply in officer_replies_with_images]
            post_dict['repost_count'] = len(user_reposts) + len(officer_replies_with_images)
            
            posts_data.append(post_dict)
        
        return format_success_response({
            'posts': posts_data,
            'total': len(posts_data)
        })
    
    except Exception as e:
        return format_error_response(f'Failed to get reposted posts: {str(e)}', 500)
