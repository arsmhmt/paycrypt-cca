"""
Client Wallet configuration Model
Handles both commission-based (Type 1) and flat-rate custom wallet (Type 2) clients
"""

from ..extensions import db
from datetime import datetime
from enum import Enum
from decimal import Decimal
from .base import BaseModel
import json

class WalletType(Enum):
    PLATFORM_BINANCE = 'platform_binance'  # Type 1: Uses our Binance wallet
    CUSTOM_API = 'custom_api'               # Type 2: Uses their own wallet API
    CUSTOM_MANUAL = 'custom_manual'         # Type 2: Manual wallet management

class WalletStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    PENDING_VERIFICATION = 'pending_verification'
    ERROR = 'error'

class PricingPlan(Enum):
    COMMISSION = 'commission'               # Type 1: Commission-based
    FLAT_RATE = 'flat_rate'                # Type 2: Flat monthly/yearly fee

class ClientWallet(BaseModel):
    __tablename__ = 'client_wallets'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Wallet configuration
    wallet_type = db.Column(db.Enum(WalletType), nullable=False)
    wallet_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(WalletStatus), default=WalletStatus.PENDING_VERIFICATION)
    
    # API configuration (for Type 2 clients)
    api_key = db.Column(db.String(500))  # Encrypted
    api_secret = db.Column(db.String(500))  # Encrypted
    api_endpoint = db.Column(db.String(255))  # Custom API endpoint
    webhook_url = db.Column(db.String(255))
    webhook_secret = db.Column(db.String(255))
    
    # Supported Cryptocurrencies (JSON array)
    supported_currencies = db.Column(db.JSON)  # ['BTC', 'ETH', 'USDT', etc.]
    
    # configuration Settings
    settings = db.Column(db.JSON)  # Custom wallet settings
    
    # Monitoring
    last_sync_at = db.Column(db.DateTime)
    last_balance_check = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Relationships
    client = db.relationship('Client', back_populates='wallets')
    
    def __repr__(self):
        return f'<ClientWallet {self.wallet_name} - {self.wallet_type.value}>'

class ClientPricingPlan(BaseModel):
    __tablename__ = 'client_pricing_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Pricing configuration
    plan_type = db.Column(db.Enum(PricingPlan), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    
    # Commission-based pricing (Type 1)
    deposit_commission_rate = db.Column(db.Numeric(precision=5, scale=4))  # 0.035 = 3.5%
    withdrawal_commission_rate = db.Column(db.Numeric(precision=5, scale=4))  # 0.015 = 1.5%
    
    # Flat-rate pricing (Type 2)
    flat_rate_amount = db.Column(db.Numeric(precision=10, scale=2))  # Monthly/yearly fee
    billing_cycle = db.Column(db.String(20))  # 'monthly', 'yearly'
    
    # Limits and Features
    monthly_transaction_limit = db.Column(db.Integer)
    monthly_volume_limit = db.Column(db.Numeric(precision=18, scale=8))
    features = db.Column(db.JSON)  # List of enabled features
    
    # Billing
    is_active = db.Column(db.Boolean, default=True)
    next_billing_date = db.Column(db.DateTime)
    last_payment_date = db.Column(db.DateTime)
    
    # Relationships
    client = db.relationship('Client', back_populates='pricing_plan')
    
    def __repr__(self):
        return f'<ClientPricingPlan {self.plan_name} - {self.plan_type.value}>'

class WalletTransaction(BaseModel):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('client_wallets.id'), nullable=False)
    
    # Transaction Details
    transaction_hash = db.Column(db.String(255))
    currency = db.Column(db.String(10))
    amount = db.Column(db.Numeric(precision=18, scale=8))
    fee = db.Column(db.Numeric(precision=18, scale=8))
    from_address = db.Column(db.String(255))
    to_address = db.Column(db.String(255))
    
    # Status and Metadata
    status = db.Column(db.String(20))
    confirmations = db.Column(db.Integer, default=0)
    block_number = db.Column(db.Integer)
    raw_data = db.Column(db.JSON)  # Full API response
    
    # Relationships
    wallet = db.relationship('ClientWallet', backref='transactions')
    
    def __repr__(self):
        return f'<WalletTransaction {self.transaction_hash}>'
