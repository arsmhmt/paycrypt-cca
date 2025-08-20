from datetime import datetime
from enum import Enum
from ..extensions import db

class ClientSettingKey(Enum):
    """Keys for client-specific settings"""
    THEME = 'theme'
    LANGUAGE = 'language'
    TIMEZONE = 'timezone'
    CURRENCY = 'currency'
    NOTIFICATION_EMAIL = 'notification_email'
    NOTIFICATION_SMS = 'notification_sms'
    NOTIFICATION_PUSH = 'notification_push'
    API_RATE_LIMIT = 'api_rate_limit'
    AUTO_CONFIRM_WITHDRAWAL = 'auto_confirm_withdrawal'
    MIN_WITHDRAWAL_AMOUNT = 'min_withdrawal_amount'
    MAX_WITHDRAWAL_AMOUNT = 'max_withdrawal_amount'
    WITHDRAWAL_FEE = 'withdrawal_fee'
    WITHDRAWAL_FEE_TYPE = 'withdrawal_fee_type'  # 'fixed' or 'percentage'
    DEPOSIT_FEE = 'deposit_fee'
    DEPOSIT_FEE_TYPE = 'deposit_fee_type'  # 'fixed' or 'percentage'
    
    @classmethod
    def get_all_keys(cls):
        """Get all setting keys as a list"""
        return [key.value for key in cls]

class ClientSetting(db.Model):
    """Client-specific settings"""
    __tablename__ = 'client_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    key = db.Column(db.Enum(ClientSettingKey), nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    client = db.relationship('Client', backref=db.backref('client_settings', lazy=True))
    
    def __repr__(self):
        return f'<ClientSetting {self.client_id}:{self.key.value}={self.value}>'
    
    @classmethod
    def get_setting(cls, client_id, key, default=None):
        """Get a setting value for a client"""
        if not isinstance(key, ClientSettingKey):
            try:
                key = ClientSettingKey(key)
            except ValueError:
                return default
                
        setting = cls.query.filter_by(client_id=client_id, key=key).first()
        return setting.value if setting else default
    
    @classmethod
    def set_setting(cls, client_id, key, value, description=None, is_public=False):
        """Set a setting value for a client"""
        if not isinstance(key, ClientSettingKey):
            key = ClientSettingKey(key)
            
        setting = cls.query.filter_by(client_id=client_id, key=key).first()
        
        if setting:
            setting.value = str(value)
            if description is not None:
                setting.description = description
            if is_public is not None:
                setting.is_public = is_public
        else:
            setting = cls(
                client_id=client_id,
                key=key,
                value=str(value),
                description=description,
                is_public=is_public
            )
            db.session.add(setting)
        
        db.session.commit()
        return setting
    
    @classmethod
    def get_all_settings(cls, client_id, include_private=False):
        """Get all settings for a client"""
        query = cls.query.filter_by(client_id=client_id)
        if not include_private:
            query = query.filter_by(is_public=True)
        return {setting.key: setting.value for setting in query.all()}
    
    @classmethod
    def delete_setting(cls, client_id, key):
        """Delete a setting for a client"""
        if not isinstance(key, ClientSettingKey):
            key = ClientSettingKey(key)
            
        setting = cls.query.filter_by(client_id=client_id, key=key).first()
        if setting:
            db.session.delete(setting)
            db.session.commit()
            return True
        return False
