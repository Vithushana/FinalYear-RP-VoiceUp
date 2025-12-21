"""
Database Migration Script
Adds indexes to existing database without losing data
This script adds the performance indexes defined in models.py
"""
from app import create_app
from models import db
import sqlite3
import os

# Create app instance
app = create_app()

def get_existing_indexes(cursor, table_name):
    """Get list of existing indexes for a table"""
    cursor.execute(f"PRAGMA index_list({table_name})")
    return [row[1] for row in cursor.fetchall()]

def index_exists(cursor, table_name, index_name):
    """Check if an index already exists"""
    existing_indexes = get_existing_indexes(cursor, table_name)
    return index_name in existing_indexes

def migrate_database():
    """Add indexes to existing database"""
    with app.app_context():
        try:
            print("=" * 60)
            print("📊 DATABASE MIGRATION - ADDING PERFORMANCE INDEXES")
            print("=" * 60)
            
            # Get database path
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            
            if not os.path.exists(db_path):
                print(f"\n❌ Database not found at: {db_path}")
                print("   Creating new database with indexes...")
                db.create_all()
                print("✅ New database created with all indexes!")
                return
            
            print(f"\n📁 Database: {db_path}")
            print("\n🔄 Adding indexes...\n")
            
            # Connect directly to SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            indexes_added = 0
            indexes_skipped = 0
            
            # Define all indexes to add
            indexes = [
                # Posts table indexes (7 indexes)
                ("posts", "idx_post_user_id", "CREATE INDEX IF NOT EXISTS idx_post_user_id ON posts(user_id)"),
                ("posts", "idx_post_province", "CREATE INDEX IF NOT EXISTS idx_post_province ON posts(province)"),
                ("posts", "idx_post_district", "CREATE INDEX IF NOT EXISTS idx_post_district ON posts(district)"),
                ("posts", "idx_post_region", "CREATE INDEX IF NOT EXISTS idx_post_region ON posts(region)"),
                ("posts", "idx_post_status", "CREATE INDEX IF NOT EXISTS idx_post_status ON posts(status)"),
                ("posts", "idx_post_assigned_officer", "CREATE INDEX IF NOT EXISTS idx_post_assigned_officer ON posts(assigned_officer_id)"),
                ("posts", "idx_post_created_at", "CREATE INDEX IF NOT EXISTS idx_post_created_at ON posts(created_at)"),
                
                # Users table indexes (4 indexes)
                ("users", "idx_user_is_officer", "CREATE INDEX IF NOT EXISTS idx_user_is_officer ON users(is_officer)"),
                ("users", "idx_user_officer_province", "CREATE INDEX IF NOT EXISTS idx_user_officer_province ON users(officer_province)"),
                ("users", "idx_user_officer_district", "CREATE INDEX IF NOT EXISTS idx_user_officer_district ON users(officer_district)"),
                ("users", "idx_user_officer_region", "CREATE INDEX IF NOT EXISTS idx_user_officer_region ON users(officer_region)"),
                
                # Notifications table indexes (4 indexes)
                ("notifications", "idx_notification_user_id", "CREATE INDEX IF NOT EXISTS idx_notification_user_id ON notifications(user_id)"),
                ("notifications", "idx_notification_post_id", "CREATE INDEX IF NOT EXISTS idx_notification_post_id ON notifications(post_id)"),
                ("notifications", "idx_notification_read", "CREATE INDEX IF NOT EXISTS idx_notification_read ON notifications(read)"),
                ("notifications", "idx_notification_created_at", "CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notifications(created_at)"),
            ]
            
            # Add each index
            for table_name, index_name, create_sql in indexes:
                if index_exists(cursor, table_name, index_name):
                    print(f"   ⏭️  {index_name} - Already exists")
                    indexes_skipped += 1
                else:
                    cursor.execute(create_sql)
                    print(f"   ✅ {index_name} - Added")
                    indexes_added += 1
            
            # Commit changes
            conn.commit()
            conn.close()
            
            print("\n" + "=" * 60)
            print("✅ DATABASE MIGRATION COMPLETE!")
            print("=" * 60)
            
            print(f"\n📊 Summary:")
            print(f"   • Indexes added: {indexes_added}")
            print(f"   • Indexes already existed: {indexes_skipped}")
            print(f"   • Total indexes: {indexes_added + indexes_skipped}")
            
            print("\n🚀 Your database is now optimized for better performance!")
            print("   These indexes will speed up:")
            print("   • Officer dashboard queries")
            print("   • Post filtering by status and region")
            print("   • Notification retrieval")
            print("   • User authentication checks")
            
            print("\n" + "=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error during migration: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    migrate_database()
