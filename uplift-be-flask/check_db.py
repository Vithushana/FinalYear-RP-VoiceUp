from db import db
import json
from bson import ObjectId

def check_db_structure():
    print("🔍 Checking database structure...")
    
    # Get one issue from each status
    statuses = ["Seen", "Verified", "In Progress", "On Hold", "Completed", "Archived", "Closed"]
    
    for status in statuses:
        issue = db.issues.find_one({"status": status})
        if issue:
            print(f"\n📋 Sample {status} issue structure:")
            # Convert ObjectId to string for JSON serialization
            issue_copy = {}
            for key, value in issue.items():
                if isinstance(value, ObjectId):
                    issue_copy[key] = str(value)
                else:
                    issue_copy[key] = value
            print(json.dumps(issue_copy, indent=2, default=str))
            break
    
    # Count issues by status
    print("\n📊 Issue counts by status:")
    for status in statuses:
        count = db.issues.count_documents({"status": status})
        print(f"   {status}: {count}")
    
    total = db.issues.count_documents({})
    print(f"\n📈 Total issues: {total}")

if __name__ == "__main__":
    check_db_structure()