from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
from db import db

# Collections
issues_collection = db["issues"]
stats_collection = db["stats"]

class IssueModel:
    @staticmethod
    def create_issue(data: Dict) -> str:
        """Create a new issue and return its ID"""
        issue = {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "location": data.get("location", ""),
            "type": data.get("type", ""),
            "impact": data.get("impact", "Medium"),
            "severity": data.get("severity", "Moderate"),
            "status": data.get("status", "Seen"),
            "reporter_id": data.get("reporter_id"),
            "reporter_name": data.get("reporter_name", "Anonymous"),
            "images": data.get("images", []),
            "coordinates": data.get("coordinates", {}),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_reposted": False,
            "matching_posts_count": data.get("matching_posts_count", 0)
        }
        
        result = issues_collection.insert_one(issue)
        return str(result.inserted_id)
    
    @staticmethod
    def get_issues(limit: int = 50, skip: int = 0, status: Optional[str] = None) -> List[Dict]:
        """Get issues with optional filtering"""
        query = {}
        if status:
            query["status"] = status
            
        cursor = issues_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        issues = []
        
        for issue in cursor:
            issue["_id"] = str(issue["_id"])
            issue["id"] = issue["_id"]  # Add id field for frontend compatibility
            
            # Format time as relative time
            if "created_at" in issue:
                time_diff = datetime.utcnow() - issue["created_at"]
                if time_diff.days > 0:
                    issue["time"] = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    issue["time"] = f"{hours} hour{'s' if hours > 1 else ''} ago"
                else:
                    minutes = time_diff.seconds // 60
                    issue["time"] = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            
            # Determine if it has images
            issue["hasImage"] = len(issue.get("images", [])) > 0
            issue["image"] = issue.get("images", [None])[0]  # First image for preview
            
            issues.append(issue)
        
        return issues
    
    @staticmethod
    def get_issue_by_id(issue_id: str) -> Optional[Dict]:
        """Get a single issue by ID"""
        try:
            issue = issues_collection.find_one({"_id": ObjectId(issue_id)})
            if issue:
                issue["_id"] = str(issue["_id"])
                issue["id"] = issue["_id"]
                
                # Format created_at as date string
                if "created_at" in issue:
                    issue["posted"] = issue["created_at"].strftime("%Y-%m-%d")
                
                issue["hasImage"] = len(issue.get("images", [])) > 0
                issue["mainImage"] = issue.get("images", [None])[0]
                issue["thumbnails"] = issue.get("images", [])[:3]  # First 3 as thumbnails
                
                return issue
        except:
            pass
        return None
    
    @staticmethod
    def update_issue_status(issue_id: str, status: str) -> bool:
        """Update issue status"""
        try:
            result = issues_collection.update_one(
                {"_id": ObjectId(issue_id)},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    @staticmethod
    def get_reposted_issues(limit: int = 50, skip: int = 0) -> List[Dict]:
        """Get reposted issues"""
        cursor = issues_collection.find({"is_reposted": True}).sort("created_at", -1).skip(skip).limit(limit)
        issues = []
        
        for issue in cursor:
            issue["_id"] = str(issue["_id"])
            issue["id"] = issue["_id"]
            
            # Format time as relative time
            if "created_at" in issue:
                time_diff = datetime.utcnow() - issue["created_at"]
                if time_diff.days > 0:
                    issue["time"] = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    issue["time"] = f"{hours} hour{'s' if hours > 1 else ''} ago"
                else:
                    minutes = time_diff.seconds // 60
                    issue["time"] = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            
            issue["hasImage"] = len(issue.get("images", [])) > 0
            issue["image"] = issue.get("images", [None])[0]
            
            issues.append(issue)
        
        return issues
    
    @staticmethod
    def update_achievement(issue_id: str, achievement_text: str) -> bool:
        """Update achievement text for a completed issue"""
        try:
            result = issues_collection.update_one(
                {"_id": ObjectId(issue_id)},
                {
                    "$set": {
                        "achievement": achievement_text,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    


class StatsModel:
    @staticmethod
    def get_dashboard_stats() -> Dict:
        """Get dashboard statistics"""
        # Count issues by status
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        
        status_counts = {}
        for result in issues_collection.aggregate(pipeline):
            status_counts[result["_id"]] = result["count"]
        
        # Calculate totals
        total_issues = issues_collection.count_documents({})
        pending_issues = status_counts.get("Seen", 0) + status_counts.get("Verified", 0)
        reported_issues = status_counts.get("Seen", 0)
        verified = status_counts.get("Verified", 0)
        on_hold = status_counts.get("On Hold", 0)
        in_progress = status_counts.get("In Progress", 0)
        completed = status_counts.get("Completed", 0)
        
        stats = {
            "pending_issues": pending_issues,
            "reported_issues": reported_issues,
            "verified": verified,
            "on_hold": on_hold,
            "in_progress": in_progress,
            "achievements": completed,  # Completed issues as achievements
            "total_issues": total_issues
        }
        
        return stats
    
    @staticmethod
    def update_stats():
        """Update cached stats (can be called periodically)"""
        stats = StatsModel.get_dashboard_stats()
        stats["updated_at"] = datetime.utcnow()
        
        stats_collection.replace_one(
            {"type": "dashboard"},
            {"type": "dashboard", **stats},
            upsert=True
        )