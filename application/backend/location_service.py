"""
Location Service for GPS-based routing
Converts GPS coordinates to province/district and assigns posts to correct officers
"""
from models import db, User, Post, Notification
from datetime import datetime
from geopy.geocoders import Nominatim
from region_mapping import get_region_from_locality

# Sri Lanka province/district boundaries (simplified GPS ranges)
# Format: {province: {district: {'lat_range': (min, max), 'lng_range': (min, max)}}}
PROVINCE_DISTRICTS = {
    'Central Province': {
        'Kandy': {'lat_range': (7.0, 7.5), 'lng_range': (80.5, 81.0)},
        'Matale': {'lat_range': (7.3, 7.7), 'lng_range': (80.5, 80.9)},
        'Nuwara Eliya': {'lat_range': (6.8, 7.2), 'lng_range': (80.6, 81.0)},
    },
    'Western Province': {
        'Colombo': {'lat_range': (6.8, 7.0), 'lng_range': (79.8, 80.0)},
        'Gampaha': {'lat_range': (6.9, 7.2), 'lng_range': (79.9, 80.2)},
        'Kalutara': {'lat_range': (6.5, 6.8), 'lng_range': (79.9, 80.3)},
    },
    'Southern Province': {
        'Galle': {'lat_range': (6.0, 6.2), 'lng_range': (80.1, 80.3)},
        'Matara': {'lat_range': (5.9, 6.1), 'lng_range': (80.5, 80.7)},
        'Hambantota': {'lat_range': (6.0, 6.3), 'lng_range': (81.0, 81.3)},
    },
    'Northern Province': {
        'Jaffna': {'lat_range': (9.5, 9.8), 'lng_range': (80.0, 80.1)},
        'Kilinochchi': {'lat_range': (9.3, 9.5), 'lng_range': (80.3, 80.5)},
        'Mannar': {'lat_range': (8.9, 9.1), 'lng_range': (79.8, 80.0)},
        'Vavuniya': {'lat_range': (8.7, 8.9), 'lng_range': (80.4, 80.6)},
        'Mullaitivu': {'lat_range': (9.2, 9.4), 'lng_range': (80.7, 80.9)},
    },
    'Eastern Province': {
        'Trincomalee': {'lat_range': (8.5, 8.7), 'lng_range': (81.1, 81.3)},
        'Batticaloa': {'lat_range': (7.7, 7.9), 'lng_range': (81.6, 81.8)},
        'Ampara': {'lat_range': (7.2, 7.4), 'lng_range': (81.6, 81.8)},
    },
    'North Western Province': {
        'Kurunegala': {'lat_range': (7.4, 7.6), 'lng_range': (80.3, 80.5)},
        'Puttalam': {'lat_range': (8.0, 8.2), 'lng_range': (79.8, 80.0)},
    },
    'North Central Province': {
        'Anuradhapura': {'lat_range': (8.3, 8.5), 'lng_range': (80.3, 80.5)},
        'Polonnaruwa': {'lat_range': (7.9, 8.1), 'lng_range': (81.0, 81.2)},
    },
    'Uva Province': {
        'Badulla': {'lat_range': (6.9, 7.1), 'lng_range': (81.0, 81.2)},
        'Monaragala': {'lat_range': (6.8, 7.0), 'lng_range': (81.3, 81.5)},
    },
    'Sabaragamuwa Province': {
        'Ratnapura': {'lat_range': (6.6, 6.8), 'lng_range': (80.3, 80.5)},
        'Kegalle': {'lat_range': (7.2, 7.4), 'lng_range': (80.3, 80.5)},
    },
}


def get_location_from_gps(latitude, longitude):
    """
    Convert GPS coordinates to province, district, and region
    
    Args:
        latitude (float): GPS latitude
        longitude (float): GPS longitude
    
    Returns:
        tuple: (province, district, region) or (None, None, None) if not found
    """
    if not latitude or not longitude:
        return None, None, None
    
    try:
        # Use Nominatim for reverse geocoding
        geolocator = Nominatim(user_agent="voiceup_app")
        location = geolocator.reverse(f"{latitude}, {longitude}", language='en')
        
        if location and location.raw.get('address'):
            address = location.raw['address']
            
            # Extract province (state)
            province = address.get('state', '')
            
            # Extract district - try multiple fields
            district = address.get('county', '') or address.get('state_district', '') or address.get('city', '')
            
            # Normalize district name (remove " District" suffix)
            if district and district.endswith(' District'):
                district = district.replace(' District', '')
            
            # Extract locality for region matching
            locality = (address.get('suburb') or 
                       address.get('neighbourhood') or 
                       address.get('city_district') or 
                       address.get('municipality') or
                       address.get('town') or  # Added town
                       address.get('city', ''))
            
            # Special handling for Malabe area (part of Colombo district, Kaduwela MC)
            if locality and 'malabe' in locality.lower():
                district = 'Colombo'  # Ensure district is Colombo
                region = 'Kaduwela MC'  # Directly set region
            else:
                # Get matched region from mapping
                region = get_region_from_locality(locality, district)
            
            print(f"📍 GPS: ({latitude}, {longitude}) → {province}, {district}, {region}")
            print(f"   Locality extracted: {locality}")
            return province, district, region
    
    except Exception as e:
        print(f"❌ Geocoding error: {str(e)}")
    
    # Fallback to coordinate-based matching
    for province, districts in PROVINCE_DISTRICTS.items():
        for district, bounds in districts.items():
            lat_min, lat_max = bounds['lat_range']
            lng_min, lng_max = bounds['lng_range']
            
            if (lat_min <= latitude <= lat_max and 
                lng_min <= longitude <= lng_max):
                return province, district, None
    
    return None, None, None


def find_officer_for_location(province, district, region=None, issue_type='Road'):
    """
    Find the officer responsible for a specific province/district/region and issue type
    
    Args:
        province (str): Province name
        district (str): District name
        region (str): Region/MC/UC name (optional)
        issue_type (str): 'Road' or 'Garbage'
    
    Returns:
        User: Officer user object or None if not found
    """
    if not province or not district:
        return None
    
    # Determine officer type based on issue type
    officer_type = 'garbage' if issue_type == 'Garbage' else 'road'
    
    # Try to find officer with matching region first (most specific)
    if region:
        officer = User.query.filter_by(
            is_officer=True,
            officer_province=province,
            officer_district=district,
            officer_region=region,
            officer_type=officer_type
        ).first()
        
        if officer:
            print(f"✅ Found region-specific officer: {officer.username} ({region})")
            return officer
    
    # Fallback: Find officer with matching province/district and type (no region specified)
    officer = User.query.filter_by(
        is_officer=True,
        officer_province=province,
        officer_district=district,
        officer_type=officer_type
    ).first()
    
    if officer:
        print(f"✅ Found district-level officer: {officer.username}")
        return officer
    
    # Final fallback: Any officer for that location (ignore type)
    officer = User.query.filter_by(
        is_officer=True,
        officer_province=province,
        officer_district=district
    ).first()
    
    if officer:
        print(f"⚠️  Using fallback officer: {officer.username} (type mismatch)")
    
    return officer


def assign_officer_to_post(post):
    """
    Assign the correct officer to a post based on its location, region, and issue type
    
    Args:
        post (Post): Post object to assign
    
    Returns:
        User: Assigned officer or None if no officer found
    """
    # If GPS coordinates are available, use them
    if post.latitude and post.longitude:
        province, district, region = get_location_from_gps(post.latitude, post.longitude)
        
        if province and district:
            post.province = province
            post.district = district
            post.region = region
    
    # If we have province/district (either from GPS or manual), find officer
    if post.province and post.district:
        # Find officer based on location, region, AND issue type
        officer = find_officer_for_location(
            post.province, 
            post.district,
            post.region,  # Include region for specific matching
            post.issue_type
        )
        
        if officer:
            post.assigned_officer_id = officer.id
            
            # Create notification for officer with issue type context
            issue_description = f"{post.issue_type}"
            if post.issue_type == 'Road' and post.road_type:
                issue_description = f"{post.road_type} (Road)"
            
            location_str = f"{post.region}, {post.district}" if post.region else post.district
            
            create_officer_notification(
                officer_id=officer.id,
                post_id=post.id,
                notification_type='new_issue',
                title='New Issue in Your Area',
                message=f'New {issue_description} reported in {location_str}: {post.title}'
            )
            
            return officer
    
    return None


def create_officer_notification(officer_id, post_id, notification_type, title, message):
    """
    Create a notification for an officer
    
    Args:
        officer_id (int): Officer's user ID
        post_id (int): Related post ID
        notification_type (str): Type of notification
        title (str): Notification title
        message (str): Notification message
    """
    notification = Notification(
        user_id=officer_id,
        post_id=post_id,
        title=title,
        message=message,
        type=notification_type,
        read=False
    )
    db.session.add(notification)
    db.session.commit()


def create_user_notification(user_id, post_id, notification_type, title, message):
    """
    Create a notification for a user
    
    Args:
        user_id (int): User's ID
        post_id (int): Related post ID
        notification_type (str): Type of notification
        title (str): Notification title
        message (str): Notification message
    """
    notification = Notification(
        user_id=user_id,
        post_id=post_id,
        title=title,
        message=message,
        type=notification_type,
        read=False
    )
    db.session.add(notification)
    db.session.commit()


def notify_status_change(post, old_status, new_status):
    """
    Notify user when post status changes
    
    Args:
        post (Post): Post object
        old_status (str): Previous status
        new_status (str): New status
    """
    status_messages = {
        'seen': 'Your post has been seen by authorities',
        'verified': 'Your post has been verified',
        'hold': 'Your post is on hold',
        'in_progress': 'Work has started on your issue!',
        'completed': 'Your issue has been completed!',
        'closed': 'Your post has been closed',
    }
    
    message = status_messages.get(new_status, f'Your post status changed to {new_status}')
    
    create_user_notification(
        user_id=post.user_id,
        post_id=post.id,
        notification_type='status_change',
        title='Post Status Updated',
        message=message
    )


def notify_officer_reply(post, officer_name):
    """
    Notify user when officer replies to their post
    
    Args:
        post (Post): Post object
        officer_name (str): Name of the officer who replied
    """
    desc = post.description[:50] + '...' if len(post.description) > 50 else post.description
    create_user_notification(
        user_id=post.user_id,
        post_id=post.id,
        notification_type='reply',
        title='Official Reply Received',
        message=f'{officer_name} replied to your post "{desc}"'
    )


def get_officer_stats(officer_id):
    """
    Get dashboard statistics for an officer
    
    Args:
        officer_id (int): Officer's user ID
    
    Returns:
        dict: Statistics by status
    """
    # Get officer's region details
    officer = User.query.get(officer_id)
    if not officer or not officer.is_officer:
        return {
            'unseen': 0,
            'seen': 0,
            'verified': 0,
            'hold': 0,
            'in_progress': 0,
            'completed': 0,
            'closed': 0,
            'total': 0,
        }
    
    # Get posts in officer's region AND matching officer's type (Road/Garbage)
    posts = Post.query.filter_by(
        province=officer.officer_province,
        district=officer.officer_district,
        region=officer.officer_region
    )
    
    # CRITICAL FIX: Filter by officer type (Road/Garbage)
    # NOTE: officer_type is lowercase ('road', 'garbage') but issue_type is capitalized ('Road', 'Garbage')
    if officer.officer_type:
        # Capitalize officer_type to match issue_type format
        issue_type_filter = officer.officer_type.capitalize()
        posts = posts.filter_by(issue_type=issue_type_filter)
        print(f"📊 Dashboard stats filtered for {officer.username} (Type: {officer.officer_type} -> {issue_type_filter})")
    
    # Get achievements count for the officer's region AND type
    from models import Achievement
    achievements_query = Achievement.query.join(Post).filter(
        Post.province == officer.officer_province,
        Post.district == officer.officer_district,
        Post.region == officer.officer_region
    )
    
    # Also filter achievements by officer type
    if officer.officer_type:
        issue_type_filter = officer.officer_type.capitalize()
        achievements_query = achievements_query.filter(Post.issue_type == issue_type_filter)
    
    achievements_count = achievements_query.count()
    
    stats = {
        'unseen': posts.filter_by(status='submitted').count(),
        'seen': posts.filter_by(status='seen').count(),
        'verified': posts.filter_by(status='verified').count(),
        'hold': posts.filter_by(status='hold').count(),
        'in_progress': posts.filter_by(status='in_progress').count(),
        'completed': posts.filter_by(status='completed').count(),
        'closed': posts.filter_by(status='closed').count(),
        'achievements': achievements_count,
        'total': posts.count(),
    }
    
    return stats
