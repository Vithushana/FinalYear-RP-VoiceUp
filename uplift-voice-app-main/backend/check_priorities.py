import pymongo
from pymongo import MongoClient
import random

client = MongoClient('mongodb://localhost:27017/')
db = client['voiceup']
collection = db['issues']

# Check current priority distribution
priorities = list(collection.aggregate([
    {'$group': {'_id': '$priority', 'count': {'$sum': 1}}}
]))

print('Current priority distribution:')
for p in priorities:
    print(f'{p["_id"]}: {p["count"]} issues')

print('\nSample issues with their priorities:')
for issue in collection.find().limit(10):
    print(f'ID: {issue["_id"]}, Priority: {issue.get("priority", "N/A")}, Severity: {issue.get("severity", "N/A")}, Title: {issue["title"][:50]}...')

# Update priorities to have a good mix
print('\nUpdating priorities to create a mix...')

# Get all issues
all_issues = list(collection.find())
total_issues = len(all_issues)

# Create a balanced distribution
# 30% critical (high), 50% medium, 20% low
critical_count = int(total_issues * 0.3)
medium_count = int(total_issues * 0.5)
low_count = total_issues - critical_count - medium_count

print(f'Target distribution: {critical_count} critical, {medium_count} medium, {low_count} low')

# Shuffle issues and assign new priorities
random.shuffle(all_issues)

for i, issue in enumerate(all_issues):
    if i < critical_count:
        new_priority = 'critical'
        new_severity = 'Critical'
    elif i < critical_count + medium_count:
        new_priority = 'medium'
        new_severity = 'Moderate'
    else:
        new_priority = 'low'
        new_severity = 'Low'
    
    collection.update_one(
        {'_id': issue['_id']},
        {'$set': {'priority': new_priority, 'severity': new_severity}}
    )

print('Priority update completed!')

# Check new distribution
new_priorities = list(collection.aggregate([
    {'$group': {'_id': '$priority', 'count': {'$sum': 1}}}
]))

print('\nNew priority distribution:')
for p in new_priorities:
    print(f'{p["_id"]}: {p["count"]} issues')

print('\nSample of updated issues:')
for issue in collection.find().limit(10):
    print(f'ID: {issue["_id"]}, Priority: {issue.get("priority", "N/A")}, Severity: {issue.get("severity", "N/A")}, Title: {issue["title"][:50]}...')