from models import IssueModel, StatsModel
from datetime import datetime, timedelta
import random

def add_missing_status_data():
    """Add issues for missing status types"""
    
    # Additional issues for missing statuses
    additional_issues = [
        {
            "title": "Damaged Road Sign - Fixed and Archived",
            "description": "Road sign was damaged in storm but has been repaired and archived for reference.",
            "location": "Oak Street & 2nd Avenue",
            "category": "Traffic Infrastructure",
            "priority": "low",
            "status": "Archived",
            "userName": "Mike Wilson", 
            "userMobile": "+1234567890",
            "userUploadImages": [
                "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=500",
                "https://images.unsplash.com/photo-1546942113-a6c43b63104a?w=500"
            ],
            "matchingPosts": [],
        },
        {
            "title": "Playground Safety Issue - Case Closed",
            "description": "Safety hazard at playground has been permanently addressed and case is now closed.",
            "location": "Central Park Playground",
            "category": "Public Safety",
            "priority": "medium",
            "status": "Closed",
            "userName": "Lisa Chen",
            "userMobile": "+1234567891", 
            "userUploadImages": [
                "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=500",
                "https://images.unsplash.com/photo-1577976041001-4d3b60c6d42a?w=500"
            ],
            "matchingPosts": [],
        },
        {
            "title": "Water Main Break - Archived After Repair",
            "description": "Major water main break has been fully repaired and documented for future reference.",
            "location": "Industrial District, Block 5",
            "category": "Utilities",
            "priority": "critical",
            "status": "Archived", 
            "userName": "David Rodriguez",
            "userMobile": "+1234567892",
            "userUploadImages": [
                "https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=500",
                "https://images.unsplash.com/photo-1582719471354-c4afd8b32c5d?w=500"
            ],
            "matchingPosts": [],
        },
        {
            "title": "Noise Complaint - Case Permanently Closed",
            "description": "Ongoing noise complaint has been resolved through legal channels and case is closed.",
            "location": "Residential Area, Block 12",
            "category": "Noise Control",
            "priority": "low",
            "status": "Closed",
            "userName": "Emma Thompson",
            "userMobile": "+1234567893",
            "userUploadImages": [
                "https://images.unsplash.com/photo-1590736969955-71cc94901144?w=500"
            ],
            "matchingPosts": [],
        },
        {
            "title": "Sidewalk Crack - Additional Verified Issue",
            "description": "Significant crack in sidewalk verified by inspection team, awaiting repair scheduling.",
            "location": "Business District, 7th Street",
            "category": "Pedestrian Infrastructure", 
            "priority": "medium",
            "status": "Verified",
            "userName": "James Park",
            "userMobile": "+1234567894",
            "userUploadImages": [
                "https://images.unsplash.com/photo-1566835308184-8c4e31c4c43e?w=500",
                "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=500"
            ],
            "matchingPosts": [],
        },
        {
            "title": "Parking Meter Malfunction - On Hold",
            "description": "Multiple parking meters not accepting payment. Waiting for parts delivery to complete repairs.",
            "location": "Downtown Shopping District",
            "category": "Parking Infrastructure",
            "priority": "medium", 
            "status": "On Hold",
            "userName": "Maria Garcia",
            "userMobile": "+1234567895",
            "userUploadImages": [
                "https://images.unsplash.com/photo-1575403071077-43f50b16b313?w=500"
            ],
            "matchingPosts": [],
        },
        {
            "title": "Street Cleaning Issue - Additional In Progress",
            "description": "Scheduled street cleaning equipment repair is currently in progress.",
            "location": "Maintenance Facility",
            "category": "Street Maintenance",
            "priority": "low",
            "status": "In Progress", 
            "userName": "Robert Kim",
            "userMobile": "+1234567896",
            "userUploadImages": [
                "https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=500"
            ],
            "matchingPosts": [],
        },
        {
            "title": "Bus Stop Damage - Recently Completed",
            "description": "Bus stop shelter repair has been completed successfully and inspected.",
            "location": "Metro Line 5, Stop 42",
            "category": "Public Transportation",
            "priority": "medium",
            "status": "Completed",
            "userName": "Sophie Anderson", 
            "userMobile": "+1234567897",
            "userUploadImages": [
                "https://images.unsplash.com/photo-1570125909517-53cb21c89ff2?w=500",
                "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500"
            ],
            "matchingPosts": [],
        }
    ]
    
    print("🌱 Adding missing status data...")
    created_count = 0
    
    for issue_data in additional_issues:
        # Add random time variations
        days_ago = random.randint(1, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        created_time = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        # Create issue data dict
        issue_dict = {
            "title": issue_data["title"],
            "description": issue_data["description"],
            "type": issue_data["category"],
            "location": issue_data["location"],
            "impact": "Medium",
            "severity": "Moderate" if issue_data["priority"] == "medium" else "Critical" if issue_data["priority"] == "critical" else "Minor",
            "status": issue_data["status"],
            "reporter_name": issue_data["userName"],
            "images": issue_data["userUploadImages"],
            "matching_posts_count": len(issue_data["matchingPosts"])
        }
        
        # Create issue
        result = IssueModel.create_issue(issue_dict)
        
        if result:
            print(f"✅ Created {issue_data['status']} issue: {issue_data['title']} (ID: {result})")
            created_count += 1
        else:
            print(f"❌ Failed to create issue: {issue_data['title']}")
    
    print(f"\n🎉 Added {created_count} additional issues!")
    
    # Update stats
    try:
        StatsModel.update_stats()
        print("📊 Updated dashboard statistics")
    except Exception as e:
        print(f"⚠️ Warning: Could not update stats - {e}")

if __name__ == "__main__":
    add_missing_status_data()