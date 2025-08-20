from ..extensions import db
from .base import BaseModel

class Role(BaseModel):
    """Role model for user permissions"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.JSON, default=dict)  # Store permissions as JSON
    is_default = db.Column(db.Boolean, default=False, index=True)
    
    # Relationships
    users = db.relationship('User', back_populates='role')
    
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = {}
    
    def add_permission(self, name):
        """Add a permission to the role"""
        if not self.has_permission(name):
            self.permissions[name] = True
            return True
        return False
    
    def remove_permission(self, name):
        """Remove a permission from the role"""
        if self.has_permission(name):
            del self.permissions[name]
            return True
        return False
    
    def has_permission(self, name):
        """Check if role has a specific permission"""
        return self.permissions.get(name, False)
    
    def to_dict(self):
        """Convert role to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_default': self.is_default,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Role {self.name}>'
