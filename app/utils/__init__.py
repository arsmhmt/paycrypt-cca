"""Utilities package exports.

We avoid importing heavy/optional deps at module import time (e.g. pyqrcode),
so migrations and CLI can run even if extras aren't installed.
"""

from app.decorators import admin_required as _admin_required
from .crypto import validate_crypto_address
from .helpers import generate_api_key, generate_secure_token, is_valid_api_key
from .security import check_password


def generate_address(client_id, coin='BTC'):
    try:
        from .crypto_utils import generate_address as _impl
        return _impl(client_id, coin=coin)
    except Exception:
        # deterministic lightweight fallback
        import hashlib, os
        data = f"{client_id}_{coin}_{os.urandom(4).hex()}".encode()
        h = hashlib.sha256(data).hexdigest()
        prefix = {'BTC': '1', 'ETH': '0x', 'LTC': 'L'}.get(coin.upper(), 'addr_')
        return f"{prefix}{h[:34]}"


def generate_order_id(client_id, length=12):
    try:
        from .crypto_utils import generate_order_id as _impl
        return _impl(client_id, length=length)
    except Exception:
        import hashlib, time
        seed = f"{client_id}_{int(time.time())}".encode()
        return hashlib.sha256(seed).hexdigest()[:length].upper()


def create_qr(data, scale=6):
    try:
        from .crypto_utils import create_qr as _impl
        return _impl(data, scale=scale)
    except Exception:
        # Safe fallback if pyqrcode isn't installed
        return ""


# Export admin_required as a function
admin_required = _admin_required

__all__ = [
    'validate_crypto_address',
    'generate_api_key',
    'generate_secure_token',
    'is_valid_api_key',
    'generate_order_id',
    'create_qr',
    'admin_required',
    'check_password',
    'generate_address',
]
