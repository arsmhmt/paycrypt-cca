from datetime import datetime
from enum import Enum
from app.extensions.extensions import db

class PlanType(str, Enum):
    """Types of pricing plans."""
    STANDARD = 'standard'
    PREMIUM = 'premium'
    ENTERPRISE = 'enterprise'
    CUSTOM = 'custom'

class BillingCycle(str, Enum):
    """Billing cycle options for pricing plans."""
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    BIANNUAL = 'biannual'
    ANNUAL = 'annual'
    ONE_TIME = 'one_time'

class PricingPlan(db.Model):
    """Pricing plan model for different subscription tiers."""
    __tablename__ = 'pricing_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    plan_type = db.Column(db.Enum(PlanType), nullable=False, default=PlanType.STANDARD)
    billing_cycle = db.Column(db.Enum(BillingCycle), nullable=False, default=BillingCycle.MONTHLY)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    features = db.Column(db.JSON, nullable=True)  # Store features as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', back_populates='pricing_plan', lazy='dynamic')
    
    def __repr__(self):
        return f'<PricingPlan {self.name} ({self.plan_type.value})>'
    
    def to_dict(self):
        """Convert model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'plan_type': self.plan_type.value,
            'billing_cycle': self.billing_cycle.value,
            'price': float(self.price) if self.price else 0.0,
            'currency': self.currency,
            'is_active': self.is_active,
            'features': self.features,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
