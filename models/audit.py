from ..extensions import db
from datetime import datetime
from enum import Enum

class AuditActionType(Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    STATUS_CHANGE = 'status_change'
    DOCUMENT_UPLOAD = 'document_upload'
    DOCUMENT_DELETE = 'document_delete'
    RECURRING_PAYMENT = 'recurring_payment'
    NOTIFICATION = 'notification'
    LOGIN = 'login'
    LOGOUT = 'logout'
    API_KEY_CREATED = 'api_key_created'
    API_KEY_UPDATED = 'api_key_updated'
    API_KEY_REVOKED = 'api_key_revoked'
    API_KEY_REGENERATED = 'api_key_regenerated'

class AuditTrail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(20), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='audit_trail')

    def __init__(self, user_id, action_type, entity_type, entity_id, 
                 old_value=None, new_value=None, ip_address=None, user_agent=None):
        self.user_id = user_id
        self.action_type = action_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.old_value = old_value
        self.new_value = new_value
        self.ip_address = ip_address
        self.user_agent = user_agent

    @classmethod
    def log_action(cls, user_id, action_type, entity_type, entity_id, 
                  old_value=None, new_value=None, request=None):
        """Log an audit action"""
        from flask import current_app
        
        try:
            # Ensure user_id is an integer and not None
            if user_id is None:
                current_app.logger.warning(f"Missing user_id in audit log: {action_type} {entity_type} {entity_id}")
                return None
                
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            audit = cls(
                user_id=user_id,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                old_value=old_value,
                new_value=new_value,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.add(audit)
            # Note: We don't commit here - the caller should commit the session
            return audit
        except Exception as e:
            current_app.logger.error(f"Error logging audit action: {str(e)}")
            return None

    @classmethod
    def get_audit_trail(cls, entity_type=None, entity_id=None, 
                       action_type=None, user_id=None, limit=100):
        """Get audit trail entries with filtering"""
        query = cls.query
        
        if entity_type:
            query = query.filter_by(entity_type=entity_type)
        if entity_id:
            query = query.filter_by(entity_id=entity_id)
        if action_type:
            query = query.filter_by(action_type=action_type)
        if user_id:
            query = query.filter_by(user_id=user_id)
            
        return query.order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_user_audit_trail(cls, user_id, limit=100):
        """Get audit trail for a specific user"""
        return cls.get_audit_trail(user_id=user_id, limit=limit)

    @classmethod
    def get_entity_audit_trail(cls, entity_type, entity_id, limit=100):
        """Get audit trail for a specific entity"""
        return cls.get_audit_trail(entity_type=entity_type, entity_id=entity_id, limit=limit)

    def format_action(self):
        """Format the action for display"""
        action = self.action_type.replace('_', ' ').title()
        entity = self.entity_type.replace('_', ' ').title()
        return f"{action} {entity}"

    def format_changes(self):
        """Format changes for display"""
        changes = []
        if self.old_value and self.new_value:
            for key in self.old_value.keys():
                if self.old_value[key] != self.new_value.get(key):
                    changes.append({
                        'field': key,
                        'old': self.old_value[key],
                        'new': self.new_value.get(key)
                    })
        return changes
