from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    mobile = db.Column(db.String(20))
    position = db.Column(db.String(200))
    province = db.Column(db.String(100))
    district = db.Column(db.String(100))
    is_officer = db.Column(db.Boolean, default=False, index=True)
    officer_province = db.Column(db.String(100), index=True)
    officer_district = db.Column(db.String(100), index=True)
    officer_region = db.Column(db.String(100), index=True)
    officer_title = db.Column(db.String(200))
    officer_type = db.Column(db.String(20))
    display_name = db.Column(db.String(50))
    avatar_type = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    posts = db.relationship('Post', foreign_keys='Post.user_id', backref='author', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Composite index for officer queries
    __table_args__ = (
        db.Index('idx_officer_location_type', 'is_officer', 'officer_province', 'officer_district', 'officer_region', 'officer_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'mobile': self.mobile,
            'position': self.position,
            'province': self.province,
            'district': self.district,
            'is_officer': self.is_officer,
            'officer_province': self.officer_province,
            'officer_district': self.officer_district,
            'officer_region': self.officer_region,
            'officer_type': self.officer_type,
            'officer_title': self.officer_title,
            'display_name': self.display_name,
            'avatar_type': self.avatar_type,
            'created_at': self.created_at.isoformat()
        }


class Post(db.Model):
    """Post model for user submissions"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    province = db.Column(db.String(100), index=True)
    district = db.Column(db.String(100), index=True)
    region = db.Column(db.String(100), index=True)
    issue_type = db.Column(db.String(100), nullable=False)
    road_type = db.Column(db.String(50))
    images = db.Column(db.Text)
    status = db.Column(db.String(50), default='submitted', index=True)
    assigned_officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    priority = db.Column(db.String(20), default='medium')
    component_results = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    user_verified_completion = db.Column(db.Boolean, default=False)
    completion_image = db.Column(db.Text)
    completed_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    component_result_records = db.relationship('ComponentResult', backref='post', lazy=True, cascade='all, delete-orphan')
    officer_replies = db.relationship('OfficerReply', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    shares = db.relationship('Share', backref='post', lazy=True, cascade='all, delete-orphan')
    assigned_officer = db.relationship('User', foreign_keys=[assigned_officer_id], backref=db.backref('assigned_posts', lazy=True), lazy=True, overlaps="posts,author")
    
    # Composite indexes for performance
    __table_args__ = (
        db.Index('idx_post_location_type', 'province', 'district', 'region', 'issue_type'),
        db.Index('idx_post_status_created', 'status', 'created_at'),
    )
    
    def get_images(self):
        if self.images:
            return json.loads(self.images)
        return []
    
    def set_images(self, image_list):
        self.images = json.dumps(image_list)
    
    def get_component_results(self):
        if self.component_results:
            return json.loads(self.component_results)
        return {}
    
    def set_component_results(self, results_dict):
        self.component_results = json.dumps(results_dict)
    
    def to_dict(self):
        author_display_name = self.author.display_name if self.author.display_name else self.author.username
        author_avatar = self.author.avatar_type if self.author.avatar_type else 'male_1'
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': author_display_name,
            'display_name': author_display_name,
            'avatar_type': author_avatar,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'province': self.province,
            'district': self.district,
            'region': self.region,
            'issue_type': self.issue_type,
            'road_type': self.road_type,
            'images': self.get_images(),
            'status': self.status,
            'assigned_officer_id': self.assigned_officer_id,
            'priority': self.priority,
            'component_results': self.get_component_results(),
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'reply_count': len(self.officer_replies),
            'like_count': len(self.likes),
            'comment_count': len(self.comments) + len(self.officer_replies),
            'share_count': len(self.shares)
        }


class Notification(db.Model):
    """Notification model for user alerts"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default='info')
    action_url = db.Column(db.String(255))
    read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'action_url': self.action_url,
            'read': self.read,
            'created_at': self.created_at.isoformat() + 'Z'
        }


class ComponentResult(db.Model):
    """Component result model for tracking component processing"""
    __tablename__ = 'component_results'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    component_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    result_data = db.Column(db.Text)
    processing_time = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_result_data(self):
        if self.result_data:
            return json.loads(self.result_data)
        return {}
    
    def set_result_data(self, data_dict):
        self.result_data = json.dumps(data_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'component_name': self.component_name,
            'status': self.status,
            'result_data': self.get_result_data(),
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat()
        }


class OfficerReply(db.Model):
    """Officer reply model for government responses"""
    __tablename__ = 'officer_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    officer_name = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'officer_name': self.officer_name,
            'message': self.message,
            'image': self.image,
            'created_at': self.created_at.isoformat()
        }


class Like(db.Model):
    """Like model for post likes"""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_like'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }


class Comment(db.Model):
    """Comment model for post comments"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text)
    is_repost = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'username': self.user.username,
            'text': self.text,
            'image': self.image,
            'is_repost': self.is_repost,
            'created_at': self.created_at.isoformat()
        }


class Share(db.Model):
    """Share model for tracking post shares"""
    __tablename__ = 'shares'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }


class Achievement(db.Model):
    """Achievement model for tracking completed and closed issues"""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), unique=True, nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    posted_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    before_image = db.Column(db.Text)
    after_image = db.Column(db.Text)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    post = db.relationship('Post', backref='achievement')
    officer = db.relationship('User', backref='achievements')
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'description': self.description,
            'location': self.location,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'before_image': self.before_image,
            'after_image': self.after_image,
            'officer_id': self.officer_id,
            'created_at': self.created_at.isoformat()
        }