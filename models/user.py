from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extensions.extensions import db, login_manager
from .base import BaseModel
from sqlalchemy.orm import relationship
from .subscription import Subscription


class User(BaseModel, UserMixin):
    """Base user model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(128))
    
    # Relationships
    client = db.relationship('Client', back_populates='user', uselist=False)
    audit_trail = db.relationship('AuditTrail', back_populates='user')
    
    # Role relationship
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role', back_populates='users')
    
    # Package selection
    selected_package_id = db.Column(db.Integer, db.ForeignKey('client_packages.id'), nullable=True)
    selected_package = db.relationship('ClientPackage', foreign_keys=[selected_package_id])
    
    # Subscription relationship
    subscriptions = db.relationship('Subscription', back_populates='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_client(self):
        """Check if this user is associated with a client"""
        # Direct relationship check
        if hasattr(self, 'client') and self.client is not None:
            return True
            
        # Double-check through database query
        from ..models.client import Client
        from flask import current_app
        
        try:
            client = Client.query.filter_by(user_id=self.id).first()
            if client:
                # Cache the client on the user instance to avoid repeated queries
                self.client = client
                return True
            return False
        except Exception as e:
            if current_app:
                current_app.logger.error(f"Error in is_client check for user {self.id}: {str(e)}")
            return False
    
    def is_admin(self):
        """Check if this user is an admin (either has no client association or has admin role)"""
        if hasattr(self, 'role') and self.role and hasattr(self.role, 'name'):
            return self.role.name.lower() in ['admin', 'superadmin']
        return self.client is None
        
    def has_permission(self, permission_name):
        """Check if the user has a specific permission.
        Regular users don't have any admin permissions.
        """
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'

# NOTE: user_loader is now defined in app/__init__.py to handle both User and AdminUser properly
# This prevents security issues with cross-authentication between client and admin systems
