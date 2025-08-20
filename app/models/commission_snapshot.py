from datetime import datetime
from ..extensions import db  # Changed from 'from app import db'
from .enums import CommissionSnapshottingType
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Numeric

class CommissionSnapshot(db.Model):
    __tablename__ = 'commission_snapshots'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    deposit_commission = db.Column(db.Numeric(10, 2), nullable=False)
    withdrawal_commission = db.Column(db.Numeric(10, 2), nullable=False)
    total_commission = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    client = relationship('Client', back_populates='commission_snapshot_records')

    def __repr__(self):
        return f'<CommissionSnapshot {self.id} - Client {self.client_id} ({self.period_start} to {self.period_end})>'
