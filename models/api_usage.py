from datetime import datetime
from ..extensions import db

class ApiUsage(db.Model):
    __tablename__ = 'api_usage'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)  # GET, POST, PUT, DELETE
    status_code = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.Float, nullable=False)  # in milliseconds
    request_size = db.Column(db.Integer, nullable=False)  # in bytes
    response_size = db.Column(db.Integer, nullable=False)  # in bytes
    api_key = db.Column(db.String(64), nullable=False)
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6

    def __repr__(self):
        return f'<ApiUsage {self.id} - {self.endpoint} - {self.method}>'

    @classmethod
    def get_usage_count(cls, client_id, month, year):
        """Get API usage count for a specific client, month, and year"""
        from sqlalchemy import extract, func
        return cls.query.filter(
            cls.client_id == client_id,
            extract('month', cls.timestamp) == month,
            extract('year', cls.timestamp) == year
        ).count()

    @classmethod
    def get_last_call(cls, client_id):
        """Get the last API call timestamp for a specific client"""
        last_usage = cls.query.filter_by(client_id=client_id)\
            .order_by(cls.timestamp.desc())\
            .first()
        return last_usage.timestamp if last_usage else None
