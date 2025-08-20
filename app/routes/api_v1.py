from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import hmac
from app.models.api_key import ClientApiKey
from app.models.client import Client
from app.models import Payment, WithdrawalRequest
from app.models.enums import PaymentStatus, WithdrawalStatus
from app import db
from sqlalchemy import func
import uuid

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

def api_key_required(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Missing or invalid Authorization header',
                'message': 'Include API key as Bearer token'
            }), 401
        
        api_key = auth_header.replace('Bearer ', '')
        
        # Find the API key
        key_record = ClientApiKey.query.filter_by(key=api_key, is_active=True).first()
        if not key_record:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'API key not found or inactive'
            }), 401
        
        # Check if key is expired
        if key_record.expires_at and key_record.expires_at < datetime.utcnow():
            return jsonify({
                'error': 'API key expired',
                'message': 'Please regenerate your API key'
            }), 401
        
        # Update usage stats
        key_record.last_used_at = datetime.utcnow()
        key_record.usage_count = (key_record.usage_count or 0) + 1
        db.session.commit()
        
        # Add client to request context
        request.api_client = key_record.client
        request.api_key_record = key_record
        
        return f(*args, **kwargs)
    return decorated_function

def check_permission(permission):
    """Decorator to check if API key has specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if permission not in (request.api_key_record.permissions or []):
                return jsonify({
                    'error': 'Insufficient permissions',
                    'message': f'API key requires {permission} permission'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# === AUTHENTICATION & STATUS ===
@api_v1.route('/status', methods=['GET'])
@api_key_required
def api_status():
    """Get API status and client information"""
    client = request.api_client
    
    return jsonify({
        'status': 'active',
        'timestamp': datetime.utcnow().isoformat(),
        'client': {
            'id': client.id,
            'company_name': client.company_name,
            'client_type': 'flat_rate' if client.is_flat_rate() else 'commission',
            'package': client.package.name if client.package else None
        },
        'api_key': {
            'name': request.api_key_record.name,
            'rate_limit': request.api_key_record.rate_limit,
            'usage_count': request.api_key_record.usage_count,
            'permissions': request.api_key_record.permissions
        }
    })

# === BETSLIP SPECIFIC ENDPOINTS ===
@api_v1.route('/betslip/generate', methods=['POST'])
@api_key_required
@check_permission('flat_rate:payment:create')
def generate_betslip():
    """Generate a new payment request for betslip"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'currency', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Missing required field',
                    'message': f'Field {field} is required'
                }), 400
        
        # Generate unique transaction ID
        transaction_id = f"bet_{uuid.uuid4().hex[:12]}"
        
        # Create payment record
        payment = Payment(
            client_id=request.api_client.id,
            amount=float(data['amount']),
            fiat_amount=float(data['amount']),
            crypto_currency=data['currency'],
            transaction_id=transaction_id,
            status=PaymentStatus.PENDING,
            payment_method='crypto',
            description=data.get('description', f'Betslip payment for user {data["user_id"]}')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'payment_id': payment.id,
            'transaction_id': transaction_id,
            'amount': payment.amount,
            'currency': payment.crypto_currency,
            'status': payment.status.value,
            'payment_url': f"{request.host_url}payment/{payment.id}",
            'created_at': payment.created_at.isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Betslip generation error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to generate betslip'
        }), 500

@api_v1.route('/betslip/<int:payment_id>/status', methods=['GET'])
@api_key_required
@check_permission('flat_rate:payment:read')
def betslip_status(payment_id):
    """Get betslip payment status"""
    payment = Payment.query.filter_by(
        id=payment_id, 
        client_id=request.api_client.id
    ).first()
    
    if not payment:
        return jsonify({
            'error': 'Payment not found',
            'message': 'Payment ID not found or unauthorized'
        }), 404
    
    return jsonify({
        'payment_id': payment.id,
        'transaction_id': payment.transaction_id,
        'status': payment.status.value,
        'amount': payment.amount,
        'currency': payment.crypto_currency,
        'description': payment.description,
        'created_at': payment.created_at.isoformat(),
        'completed_at': payment.updated_at.isoformat() if payment.status.value == 'completed' else None
    })

# === PAYMENT ENDPOINTS ===
@api_v1.route('/payments', methods=['GET'])
@api_key_required
@check_permission('flat_rate:payment:read')
def list_payments():
    """List payments for the client"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status = request.args.get('status')
    
    query = Payment.query.filter_by(client_id=request.api_client.id)
    
    if status:
        try:
            status_enum = PaymentStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({
                'error': 'Invalid status',
                'message': f'Status must be one of: {[s.value for s in PaymentStatus]}'
            }), 400
    
    payments = query.order_by(Payment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'payments': [{
            'id': p.id,
            'transaction_id': p.transaction_id,
            'amount': p.amount,
            'currency': p.crypto_currency,
            'status': p.status.value,
            'description': p.description,
            'created_at': p.created_at.isoformat()
        } for p in payments.items],
        'pagination': {
            'page': payments.page,
            'pages': payments.pages,
            'per_page': payments.per_page,
            'total': payments.total
        }
    })

@api_v1.route('/payments', methods=['POST'])
@api_key_required
@check_permission('flat_rate:payment:create')
def create_payment():
    """Create a new payment"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'currency']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Missing required field',
                    'message': f'Field {field} is required'
                }), 400
        
        # Generate unique transaction ID
        transaction_id = f"pay_{uuid.uuid4().hex[:12]}"
        
        # Create payment record
        payment = Payment(
            client_id=request.api_client.id,
            amount=float(data['amount']),
            fiat_amount=float(data['amount']),
            crypto_currency=data['currency'],
            transaction_id=transaction_id,
            status=PaymentStatus.PENDING,
            payment_method=data.get('payment_method', 'crypto'),
            description=data.get('description', 'API Payment')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'payment_id': payment.id,
            'transaction_id': transaction_id,
            'amount': payment.amount,
            'currency': payment.crypto_currency,
            'status': payment.status.value,
            'created_at': payment.created_at.isoformat()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Payment creation error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to create payment'
        }), 500

# === BALANCE ENDPOINTS ===
@api_v1.route('/balance', methods=['GET'])
@api_key_required
@check_permission('flat_rate:balance:read')
def get_balance():
    """Get client balance information"""
    client = request.api_client
    
    # Calculate current balance
    total_payments = db.session.query(func.sum(Payment.fiat_amount)).filter(
        Payment.client_id == client.id,
        Payment.status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    total_withdrawals = db.session.query(func.sum(WithdrawalRequest.net_amount)).filter(
        WithdrawalRequest.client_id == client.id,
        WithdrawalRequest.status == WithdrawalStatus.COMPLETED
    ).scalar() or 0
    
    current_balance = float(total_payments) - float(total_withdrawals)
    
    return jsonify({
        'balance': current_balance,
        'total_payments': float(total_payments),
        'total_withdrawals': float(total_withdrawals),
        'currency': 'USD',
        'last_updated': datetime.utcnow().isoformat()
    })

# === WITHDRAWAL ENDPOINTS ===
@api_v1.route('/withdrawals', methods=['GET'])
@api_key_required
@check_permission('flat_rate:withdrawal:read')
def list_withdrawals():
    """List withdrawal requests"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    withdrawals = WithdrawalRequest.query.filter_by(
        client_id=request.api_client.id
    ).order_by(WithdrawalRequest.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'withdrawals': [{
            'id': w.id,
            'amount': float(w.amount),
            'net_amount': float(w.net_amount) if w.net_amount else None,
            'currency': w.currency,
            'status': w.status.value,
            'wallet_address': w.user_wallet_address,
            'created_at': w.created_at.isoformat(),
            'processed_at': w.processed_at.isoformat() if w.processed_at else None
        } for w in withdrawals.items],
        'pagination': {
            'page': withdrawals.page,
            'pages': withdrawals.pages,
            'per_page': withdrawals.per_page,
            'total': withdrawals.total
        }
    })

@api_v1.route('/withdrawals', methods=['POST'])
@api_key_required
@check_permission('flat_rate:withdrawal:create')
def create_withdrawal():
    """Create a new withdrawal request"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['amount', 'currency', 'wallet_address']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'Missing required field',
                    'message': f'Field {field} is required'
                }), 400
        
        # Create withdrawal request
        withdrawal = WithdrawalRequest(
            client_id=request.api_client.id,
            amount=float(data['amount']),
            currency=data['currency'],
            user_wallet_address=data['wallet_address'],
            memo=data.get('memo'),
            note=data.get('note', 'API Withdrawal Request'),
            status=WithdrawalStatus.PENDING
        )
        
        db.session.add(withdrawal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'withdrawal_id': withdrawal.id,
            'amount': float(withdrawal.amount),
            'currency': withdrawal.currency,
            'status': withdrawal.status.value,
            'created_at': withdrawal.created_at.isoformat()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Withdrawal creation error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to create withdrawal'
        }), 500

# === ERROR HANDLERS ===
@api_v1.errorhandler(404)
def api_not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@api_v1.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The requested method is not allowed for this endpoint'
    }), 405

@api_v1.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please slow down.'
    }), 429

@api_v1.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500
