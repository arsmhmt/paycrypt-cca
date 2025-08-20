from datetime import datetime
from ..extensions import db
from .enums import PaymentStatus

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    amount = db.Column(db.Numeric(20, 8), nullable=False)
    currency = db.Column(db.String(10), nullable=False)  # 'BTC', 'ETH', etc.
    btc_value = db.Column(db.Float)  # Optional: value in BTC for reporting
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tx_hash = db.Column(db.String(100))
    block_number = db.Column(db.Integer)
    confirmation_count = db.Column(db.Integer, default=0)
    fee = db.Column(db.Numeric(20, 8))

    # Relationships
    payment = db.relationship('Payment', backref='transactions')

    def __repr__(self):
        return f'<Transaction {self.id} - {self.amount} {self.currency}>'

__all__ = ['Transaction']
