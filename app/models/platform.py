from ..extensions import db  # Changed from 'from app import db'
from datetime import datetime
from enum import Enum
from sqlalchemy import event
from .client import Client
from .payment import Payment
from .enums import PaymentStatus

class PlatformType(Enum):
    BETTING = 'betting'
    SAAS = 'saas'
    DONATION = 'donation'
    MARKETPLACE = 'marketplace'
    FREELANCER = 'freelancer'
    DAO = 'dao'

class Platform(db.Model):
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'platform_type': self.platform_type.value if self.platform_type else None,
            'webhook_url': self.webhook_url
        }

    __tablename__ = 'platforms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    platform_type = db.Column(db.Enum(PlatformType), nullable=False)
    api_key = db.Column(db.String(64), unique=True, nullable=False)
    api_secret = db.Column(db.String(64), nullable=False)
    webhook_url = db.Column(db.String(255))
    callback_url = db.Column(db.String(255))
    logo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clients = db.relationship('Client', back_populates='platform', lazy=True)
    payments = db.relationship('Payment', back_populates='platform', lazy=True)
    invoices = db.relationship('Invoice', back_populates='platform', lazy=True)
    
    def generate_api_key(self):
        """Generate a secure API key"""
        import secrets
        return secrets.token_hex(32)
    
    def verify_api_key(self, api_key):
        """Verify API key"""
        return self.api_key == api_key

class PlatformSetting(db.Model):
    __tablename__ = 'platform_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PlatformIntegration(db.Model):
    __tablename__ = 'platform_integrations'
    
    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    integration_type = db.Column(db.String(50), nullable=False)  # stripe, paypal, etc.
    config = db.Column(db.JSON, nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PlatformWebhook(db.Model):
    __tablename__ = 'platform_webhooks'
    
    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # payment_created, payment_status_changed, etc.
    url = db.Column(db.String(255), nullable=False)
    secret = db.Column(db.String(64), nullable=False)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Event listeners for audit trail
from .audit import AuditTrail, AuditActionType

@event.listens_for(Platform, 'after_insert')
@event.listens_for(Platform, 'after_update')
@event.listens_for(Platform, 'after_delete')
def log_platform_changes(mapper, connection, target):
    action = AuditActionType.CREATE if target.id is None else AuditActionType.UPDATE
    AuditTrail.log_action(
        user_id=target.id,
        action_type=action.value,
        entity_type='platform',
        entity_id=target.id,
        old_value=None,
        new_value=target.to_dict()
    )
