#!/usr/bin/env python3
"""
Usage Alert Tracking Model
Tracks sent alerts to prevent duplicates and maintain history
"""

from datetime import datetime
from app.extensions.extensions import db

class UsageAlert(db.Model):
    """Model for tracking sent usage alerts"""
    __tablename__ = 'usage_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    threshold = db.Column(db.Integer, nullable=False)  # 80, 90, 95, 100
    alert_type = db.Column(db.String(20), nullable=False)  # NOTICE, WARNING, CRITICAL, LIMIT_EXCEEDED
    usage_percentage = db.Column(db.Float, nullable=False)
    current_volume = db.Column(db.Float, nullable=False)
    max_volume = db.Column(db.Float, nullable=False)
    alert_month = db.Column(db.String(7), nullable=False)  # YYYY-MM format
    sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    email_sent = db.Column(db.Boolean, default=False)
    
    # Relationships
    client = db.relationship('Client', backref='usage_alerts')
    
    def __repr__(self):
        return f'<UsageAlert {self.client_id} {self.threshold}% {self.alert_month}>'
    
    @staticmethod
    def was_alert_sent(client_id, threshold, month=None):
        """Check if alert was already sent for this threshold this month"""
        if month is None:
            month = datetime.now().strftime('%Y-%m')
        
        return UsageAlert.query.filter_by(
            client_id=client_id,
            threshold=threshold,
            alert_month=month
        ).first() is not None
    
    @staticmethod
    def create_alert_record(client, threshold, alert_type, usage_percentage, current_volume, max_volume):
        """Create a new alert record"""
        alert = UsageAlert(
            client_id=client.id,
            threshold=threshold,
            alert_type=alert_type,
            usage_percentage=usage_percentage,
            current_volume=current_volume,
            max_volume=max_volume,
            alert_month=datetime.now().strftime('%Y-%m'),
            email_sent=True
        )
        db.session.add(alert)
        db.session.commit()
        return alert
