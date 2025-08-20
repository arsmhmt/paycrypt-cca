from ..extensions import db  # Changed from 'from app.extensions import db'
from datetime import datetime

class Currency(db.Model):
    __tablename__ = 'currencies'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)  # 'BTC', 'ETH', 'USDT'
    name = db.Column(db.String(50))
    symbol = db.Column(db.String(10))  # ₿, Ξ, $
    is_active = db.Column(db.Boolean, default=True)

class ClientBalance(db.Model):
    __tablename__ = 'client_balances'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # 'BTC', 'ETH'
    balance = db.Column(db.Float, default=0.0)
    __table_args__ = (
        db.UniqueConstraint('client_id', 'currency', name='uix_client_currency'),
    )

class ClientCommission(db.Model):
    __tablename__ = 'client_commissions'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    deposit_commission_rate = db.Column(db.Float, default=0.0)
    withdrawal_commission_rate = db.Column(db.Float, default=0.0)
    __table_args__ = (
        db.UniqueConstraint('client_id', 'currency', name='uix_commission_client_currency'),
    )

class CurrencyRate(db.Model):
    __tablename__ = 'currency_rates'
    currency = db.Column(db.String(10), primary_key=True)  # 'ETH', 'USDT', etc.
    btc_rate = db.Column(db.Float)  # 1 unit in BTC
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
