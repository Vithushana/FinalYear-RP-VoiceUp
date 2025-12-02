from models import IssueModel, StatsModel
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed database with sample issues and data"""
    
    # Sample issue data
    sample_issues = [
        {
            "title": "Broken Street Light on Main Road",
            "description": "The street light has been flickering for weeks and now completely stopped working. This creates a safety hazard for pedestrians and drivers during night time.",
            "location": "Main Road, Downtown",
            "type": "Infrastructure",
            "impact": "High",
            "severity": "Moderate",
            "status": "Seen",
            "reporter_name": "John Smith",
            "images": [
                "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=500",
                "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=500"
            ],
            "coordinates": {"lat": 40.7128, "lng": -74.0060},
            "matching_posts_count": 12,
            "is_reposted": False
        },
        {
            "title": "Pothole on Highway 101",
            "description": "Large pothole causing damage to vehicles. Multiple cars have reported tire damage. Urgent repair needed.",
            "location": "Highway 101, Mile Marker 45",
            "type": "Road Maintenance",
            "impact": "High",
            "severity": "Critical",
            "status": "Verified",
            "reporter_name": "Sarah Johnson",
            "images": [
                "https://images.unsplash.com/photo-1621544402532-6b0c2b979947?w=500",
                "https://images.unsplash.com/photo-1607473128481-baacca4b2c64?w=500"
            ],
            "coordinates": {"lat": 40.7589, "lng": -73.9851},
            "matching_posts_count": 8,
            "is_reposted": True
        },
        {
            "title": "Graffiti on Public Building",
            "description": "Vandalism on the side of the community center building. The graffiti covers a large area and needs professional cleaning.",
            "location": "Community Center, 5th Avenue",
            "type": "Vandalism",
            "impact": "Medium",
            "severity": "Minor",
            "status": "In Progress",
            "reporter_name": "Mike Davis",
            "images": [
                "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=500"
            ],
            "coordinates": {"lat": 40.7505, "lng": -73.9934},
            "matching_posts_count": 3,
            "is_reposted": False
        },
        {
            "title": "Broken Playground Equipment",
            "description": "The swing set at Central Park playground has broken chains. Children could get hurt if this isn't fixed soon.",
            "location": "Central Park Playground",
            "type": "Public Safety",
            "impact": "High",
            "severity": "Moderate",
            "status": "Completed",
            "reporter_name": "Lisa Williams",
            "images": [
                "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=500",
                "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500"
            ],
            "coordinates": {"lat": 40.7829, "lng": -73.9654},
            "matching_posts_count": 5,
            "is_reposted": False
        },
        {
            "title": "Overflowing Garbage Bin",
            "description": "The public trash bin near the bus stop has been overflowing for days. It's attracting pests and creating an unsanitary condition.",
            "location": "Bus Stop, Oak Street",
            "type": "Sanitation",
            "impact": "Medium",
            "severity": "Moderate",
            "status": "Seen",
            "reporter_name": "David Brown",
            "images": [
                "https://images.unsplash.com/photo-1586264976457-4b6b5d6a6b1a?w=500"
            ],
            "coordinates": {"lat": 40.7614, "lng": -73.9776},
            "matching_posts_count": 7,
            "is_reposted": True
        },
        {
            "title": "Water Leak on Elm Street",
            "description": "There's a significant water leak from the main pipe causing flooding on the sidewalk. Water is being wasted and creating slippery conditions.",
            "location": "Elm Street, Block 200",
            "type": "Utilities",
            "impact": "High",
            "severity": "Critical",
            "status": "On Hold",
            "reporter_name": "Emily Chen",
            "images": [
                "https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?w=500",
                "https://images.unsplash.com/photo-1582719471137-c3967ffb1c42?w=500"
            ],
            "coordinates": {"lat": 40.7282, "lng": -74.0044},
            "matching_posts_count": 15,
            "is_reposted": False
        },
        {
            "title": "Missing Stop Sign",
            "description": "The stop sign at the intersection of Pine and Cedar was knocked down during the storm last week. This intersection is very dangerous without proper signage.",
            "location": "Pine St & Cedar Ave Intersection",
            "type": "Traffic Safety",
            "impact": "Critical",
            "severity": "Critical",
            "status": "Verified",
            "reporter_name": "Robert Wilson",
            "images": [
                "https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=500"
            ],
            "coordinates": {"lat": 40.7425, "lng": -73.9928},
            "matching_posts_count": 22,
            "is_reposted": True
        },
        {
            "title": "Broken Bench in Park",
            "description": "The wooden bench near the pond has broken slats and is unsafe to sit on. Many elderly visitors use this area for rest.",
            "location": "Riverside Park, Near Pond",
            "type": "Park Maintenance",
            "impact": "Medium",
            "severity": "Minor",
            "status": "In Progress",
            "reporter_name": "Margaret Taylor",
            "images": [
                "https://images.unsplash.com/photo-1547036967-23d11aacaee0?w=500"
            ],
            "coordinates": {"lat": 40.7767, "lng": -73.9821},
            "matching_posts_count": 4,
            "is_reposted": False
        },
        {
            "title": "Illegal Dumping Site",
            "description": "Someone has been dumping construction debris and household waste behind the shopping center. This needs to be cleaned up and monitored.",
            "location": "Behind Plaza Shopping Center",
            "type": "Environmental",
            "impact": "High",
            "severity": "Moderate",
            "status": "Seen",
            "reporter_name": "Kevin Anderson",
            "images": [
                "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=500",
                "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=500"
            ],
            "coordinates": {"lat": 40.7505, "lng": -73.9864},
            "matching_posts_count": 9,
            "is_reposted": False
        },
        {
            "title": "Faulty Traffic Light",
            "description": "The traffic light at the main intersection is stuck on red in all directions. This is causing major traffic congestion during rush hours.",
            "location": "Main St & Broadway Intersection",
            "type": "Traffic Infrastructure",
            "impact": "Critical",
            "severity": "Critical",
            "status": "Completed",
            "reporter_name": "Jennifer Martinez",
            "images": [
                "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=500"
            ],
            "coordinates": {"lat": 40.7580, "lng": -73.9855},
            "matching_posts_count": 18,
            "is_reposted": True
        }
    ]
    
    print("🌱 Seeding database with sample issues...")
    
    # Create issues with varied timestamps
    for i, issue_data in enumerate(sample_issues):
        # Create issues with different timestamps (last 30 days)
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        created_time = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        issue_data['created_at'] = created_time
        issue_data['updated_at'] = created_time
        
        # Add some random reporter IDs
        issue_data['reporter_id'] = f"user_{random.randint(1000, 9999)}"
        
        try:
            from db import db
            issues_collection = db["issues"]
            result = issues_collection.insert_one(issue_data)
            print(f"✅ Created issue: {issue_data['title']} (ID: {result.inserted_id})")
        except Exception as e:
            print(f"❌ Error creating issue {issue_data['title']}: {str(e)}")
    
    # Update stats after seeding
    print("📊 Updating dashboard statistics...")
    StatsModel.update_stats()
    
    print("🎉 Database seeding completed!")
    
    # Print final stats
    stats = StatsModel.get_dashboard_stats()
    print(f"\n📈 Final Statistics:")
    print(f"   Total Issues: {stats['total_issues']}")
    print(f"   Pending: {stats['pending_issues']}")
    print(f"   Verified: {stats['verified']}")
    print(f"   In Progress: {stats['in_progress']}")
    print(f"   Completed: {stats['achievements']}")
    print(f"   On Hold: {stats['on_hold']}")

if __name__ == "__main__":
    seed_database()