from datetime import datetime, timedelta
from decimal import Decimal
from app.extensions.extensions import db
from .base import BaseModel
from .enums import PaymentStatus
from enum import Enum

class PackageActivationPayment(BaseModel):
    """
    Model for tracking package activation payments
    Clients must pay setup fee to activate their package
    """
    __tablename__ = 'package_activation_payments'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    package_id = db.Column(db.Integer, db.ForeignKey('client_packages.id'), nullable=False, index=True)
    
    # Setup fee details
    setup_fee_amount = db.Column(db.Numeric(18, 2), nullable=False, default=Decimal('1000.00'))
    setup_fee_currency = db.Column(db.String(5), nullable=False, default='USD')
    
    # Crypto payment details
    crypto_amount = db.Column(db.Numeric(18, 8), nullable=True)
    crypto_currency = db.Column(db.String(10), nullable=False, default='BTC')
    crypto_address = db.Column(db.String(255), nullable=True)  # Generated payment address
    
    # Exchange rate at time of payment
    exchange_rate = db.Column(db.Numeric(18, 8), nullable=True)
    rate_timestamp = db.Column(db.DateTime, nullable=True)
    
    # Payment status and tracking
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_hash = db.Column(db.String(255), nullable=True)  # Blockchain transaction hash
    confirmations = db.Column(db.Integer, default=0)
    required_confirmations = db.Column(db.Integer, default=1)
    
    # Activation details
    is_activated = db.Column(db.Boolean, default=False)
    activated_at = db.Column(db.DateTime, nullable=True)
    
    # Payment window
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)  # Payment must be made within this time
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional info
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    client = db.relationship('Client', backref='package_activation_payments')
    package = db.relationship('ClientPackage', backref='activation_payments')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set expiry to 24 hours from creation
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(hours=24)
    
    @property
    def is_expired(self):
        """Check if payment window has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def time_remaining(self):
        """Get remaining time for payment"""
        if self.is_expired:
            return timedelta(0)
        return self.expires_at - datetime.utcnow()
    
    def activate_package(self):
        """Activate the client's package after successful payment"""
        if self.status == PaymentStatus.COMPLETED and not self.is_activated:
            self.is_activated = True
            self.activated_at = datetime.utcnow()
            
            # Update client's package status
            if self.client:
                self.client.is_active = True
                self.client.package_id = self.package_id
            
            db.session.commit()
            return True
        return False
    
    def __repr__(self):
        return f'<PackageActivationPayment {self.id}: Client {self.client_id}, Package {self.package_id}, Status {self.status}>'

class SubscriptionBillingCycle(Enum):
    """Billing cycle options for flat-rate packages"""
    MONTHLY = 'monthly'
    ANNUAL = 'annual'

class SubscriptionStatus(Enum):
    """Subscription status options"""
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'

class FlatRateSubscriptionPayment(BaseModel):
    """
    Model for tracking flat-rate subscription payments (monthly/annual)
    Used for recurring billing of flat-rate packages
    """
    __tablename__ = 'flat_rate_subscription_payments'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    package_id = db.Column(db.Integer, db.ForeignKey('client_packages.id'), nullable=False, index=True)
    
    # Billing details
    billing_cycle = db.Column(db.Enum(SubscriptionBillingCycle), nullable=False, default=SubscriptionBillingCycle.MONTHLY)
    billing_amount = db.Column(db.Numeric(18, 2), nullable=False)
    billing_currency = db.Column(db.String(5), nullable=False, default='USD')
    
    # Billing period
    billing_period_start = db.Column(db.DateTime, nullable=False)
    billing_period_end = db.Column(db.DateTime, nullable=False)
    
    # Crypto payment details
    crypto_amount = db.Column(db.Numeric(18, 8), nullable=True)
    crypto_currency = db.Column(db.String(10), nullable=False, default='BTC')
    crypto_address = db.Column(db.String(255), nullable=True)
    
    # Exchange rate at time of payment
    exchange_rate = db.Column(db.Numeric(18, 8), nullable=True)
    rate_timestamp = db.Column(db.DateTime, nullable=True)
    
    # Payment status and tracking
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_hash = db.Column(db.String(255), nullable=True)
    confirmations = db.Column(db.Integer, default=0)
    required_confirmations = db.Column(db.Integer, default=1)
    
    # Service status
    is_service_active = db.Column(db.Boolean, default=False)
    service_activated_at = db.Column(db.DateTime, nullable=True)
    service_suspended_at = db.Column(db.DateTime, nullable=True)
    
    # Auto-renewal
    auto_renew = db.Column(db.Boolean, default=True)
    next_billing_date = db.Column(db.DateTime, nullable=True)
    
    # Payment window
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional info
    notes = db.Column(db.Text, nullable=True)
    discount_applied = db.Column(db.Numeric(5, 2), nullable=True)  # Annual discount percentage
    
    # Relationships
    client = db.relationship('Client', backref='flat_rate_payments')
    package = db.relationship('ClientPackage', backref='flat_rate_payments')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set expiry to 72 hours for subscription payments (longer window)
        if not self.expires_at:
            self.expires_at = self.created_at + timedelta(hours=72)
        
        # Set next billing date based on cycle
        if not self.next_billing_date and self.billing_period_end:
            if self.billing_cycle == SubscriptionBillingCycle.MONTHLY:
                # Add 30 days for monthly billing (simplified)
                self.next_billing_date = self.billing_period_end + timedelta(days=30)
            elif self.billing_cycle == SubscriptionBillingCycle.ANNUAL:
                # Add 365 days for annual billing (simplified)
                self.next_billing_date = self.billing_period_end + timedelta(days=365)
    
    @property
    def is_expired(self):
        """Check if payment window has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def time_remaining(self):
        """Get remaining time for payment"""
        if self.is_expired:
            return timedelta(0)
        return self.expires_at - datetime.utcnow()
    
    @property
    def is_subscription_active(self):
        """Check if subscription period is currently active"""
        now = datetime.utcnow()
        return (self.billing_period_start <= now <= self.billing_period_end 
                and self.status == PaymentStatus.COMPLETED
                and self.is_service_active)
    
    def activate_service(self):
        """Activate the client's service after successful payment"""
        if self.status == PaymentStatus.COMPLETED and not self.is_service_active:
            self.is_service_active = True
            self.service_activated_at = datetime.utcnow()
            self.service_suspended_at = None
            
            # Update client's package status
            if self.client:
                self.client.is_active = True
                self.client.package_id = self.package_id
            
            db.session.commit()
            return True
        return False
    
    def suspend_service(self):
        """Suspend service due to non-payment"""
        if self.is_service_active:
            self.is_service_active = False
            self.service_suspended_at = datetime.utcnow()
            
            # Update client status
            if self.client:
                self.client.is_active = False
            
            db.session.commit()
            return True
        return False
    
    def __repr__(self):
        return f'<FlatRateSubscriptionPayment {self.id}: Client {self.client_id}, Package {self.package_id}, {self.billing_cycle.value}>'
