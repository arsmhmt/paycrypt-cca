"""
Coin model for storing cryptocurrency metadata and configurations.
"""
from datetime import datetime
from ..extensions.extensions import db

class Coin(db.Model):
    """Model for storing cryptocurrency metadata."""
    __tablename__ = 'coin_metadata'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    decimals = db.Column(db.Integer, default=8, nullable=False)
    min_confirmations = db.Column(db.Integer, default=6, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    def to_dict(self):
        """Convert the model to a dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'is_active': self.is_active,
            'decimals': self.decimals,
            'min_confirmations': self.min_confirmations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_active_coins(cls):
        """Get all active coins."""
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def get_by_symbol(cls, symbol):
        """Get a coin by its symbol (case-insensitive)."""
        return cls.query.filter(
            db.func.lower(cls.symbol) == symbol.lower()
        ).first()
    
    @classmethod
    def get_allowed_coins(cls, package_slug):
        """
        Get coins allowed for a specific package.
        
        Args:
            package_slug (str): The package slug (e.g., 'starter_flat_rate')
            
        Returns:
            list: List of Coin objects allowed for the package
        """
        from ..config.config import config
        
        # Get the coin limit for the package
        limit = config.PACKAGE_COIN_LIMITS.get(package_slug, 15)
        
        # Get the allowed coin symbols
        allowed_symbols = config.COIN_LIST[:min(limit, len(config.COIN_LIST))]
        
        # Query the coins in the same order as COIN_LIST
        return cls.query.filter(
            cls.symbol.in_(allowed_symbols),
            cls.is_active == True
        ).order_by(
            db.func.array_position(config.COIN_LIST, cls.symbol)
        ).all()
    
    def __repr__(self):
        return f'<Coin {self.symbol} - {self.name}>'
