"""
Feature model for tracking available features in the system.
"""
from datetime import datetime
from ..extensions import db
from .base import BaseModel

class Feature(BaseModel):
    """
    Represents a feature that can be included in packages.
    """
    __tablename__ = 'features'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    feature_key = db.Column(db.String(50), unique=True, nullable=False)  # Used in code for feature checks
    category = db.Column(db.String(50))  # dashboard, api, support, analytics, etc.
    is_premium = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feature {self.name}>'
