from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Payment
from app.utils.security import rate_limit, abuse_protection
from app.utils.audit import log_api_usage, log_security_event
from app.utils.webhook_security import WebhookHandler

webhooks = Blueprint('webhooks', __name__)

# Note: This module handles inbound webhooks to PayCrypt. Outbound webhooks to merchants
# are sent using the HMAC scheme defined in app/security/signing.py from business services.

@webhooks.route('/webhook/payment_status', methods=['POST'])
@rate_limit('payment_status_webhook', limit=100)
@abuse_protection('payment_status_webhook', threshold=300)
def update_payment_status():
    """Update payment status via webhook"""
    webhook_handler = WebhookHandler()
    
    try:
        # Verify webhook signature and timestamp
        if not webhook_handler.verify_webhook(request):
            log_security_event(
                event_type='invalid_webhook_signature',
                user_id=None,
                details={'endpoint': '/webhook/payment_status'},
                ip_address=request.remote_addr
            )
            return jsonify({'error': 'Invalid webhook signature'}), 401
        
        data = request.get_json()
        order_id = data.get('order_id')
        new_status = data.get('status')

        if not order_id or not new_status:
            log_security_event(
                event_type='invalid_webhook_data',
                user_id=None,
                details={'missing_fields': ['order_id', 'status']},
                ip_address=request.remote_addr
            )
            return jsonify({'error': 'order_id and status required'}), 400

        # Log API usage
        log_api_usage(
            user_id=None,
            endpoint='/webhook/payment_status',
            method='POST',
            request_data=data,
            ip_address=request.remote_addr
        )

        payment = Payment.query.filter_by(order_id=order_id).first()

        if not payment:
            log_security_event(
                event_type='webhook_payment_not_found',
                user_id=None,
                details={'order_id': order_id},
                ip_address=request.remote_addr
            )
            return jsonify({'error': 'Payment not found'}), 404

        old_status = payment.status
        payment.status = new_status
        db.session.commit()

        # Log successful webhook processing
        log_security_event(
            event_type='payment_status_updated_via_webhook',
            user_id=payment.platform_id if hasattr(payment, 'platform_id') else None,
            details={
                'order_id': order_id,
                'old_status': old_status,
                'new_status': new_status
            },
            ip_address=request.remote_addr
        )

        return jsonify({'message': f'Payment {order_id} updated to {new_status}'}), 200
        
    except Exception as e:
        db.session.rollback()
        log_security_event(
            event_type='webhook_processing_error',
            user_id=None,
            details={'error': str(e)},
            ip_address=request.remote_addr
        )
        return jsonify({'error': 'Internal server error'}), 500
