from flask import Blueprint, render_template, abort, request, redirect
from app.models.api_key import ClientApiKey
from app.security.signing import sign_body
import json, requests
from app.models.payment_session import PaymentSession

checkout_bp = Blueprint("checkout", __name__)

@checkout_bp.route("/checkout/<ps_id>", methods=["GET", "POST"])
def checkout(ps_id):
    ps = PaymentSession.query.filter_by(public_id=ps_id).first()
    if not ps or ps.is_expired():
        abort(404)

    # --- Fiat to Crypto Conversion Logic ---
    # For demo, use static rates. In production, fetch from exchange API.
    fiat_amount = float(ps.amount)
    selected_coin = request.form.get('coin', 'USDT')
    selected_network = request.form.get('network', 'TRC20')
    # Example rates (should be dynamic)
    rates = {
        'USDT': 1.0,  # 1 USDT = 1 USD
        'BTC': 65000.0,  # 1 BTC = 65,000 USD
        'ETH': 3500.0,   # 1 ETH = 3,500 USD
    }
    coin_rate = rates.get(selected_coin, 1.0)
    crypto_amount = round(fiat_amount / coin_rate, 8)

    # --- Generate Deposit Address ---
    from app.utils import generate_address, create_qr
    deposit_address = generate_address(ps.client_id, coin=selected_coin)
    qr_code = create_qr(deposit_address)

    # --- Countdown Timer ---
    expires_at = ps.expires_at
    now = datetime.utcnow()
    seconds_left = int((expires_at - now).total_seconds())
    if seconds_left < 0:
        seconds_left = 0

    if request.method == 'POST':
        ps.status = 'pending'
        from app.extensions import db
        db.session.commit()
        # Fire webhook to merchant if configured
        if ps.webhook_url:
            key_record = ClientApiKey.query.filter_by(client_id=ps.client_id, is_active=True).first()
            if key_record and key_record.secret_key:
                payload = {
                    "type": "payment.succeeded",
                    "id": f"evt_{ps.id}",
                    "data": {
                        "payment_session_id": ps.id,
                        "order_id": ps.order_id,
                        "amount": str(ps.amount),
                        "currency": ps.currency,
                        "status": "succeeded"
                    },
                    "created": int(__import__('time').time())
                }
                body = json.dumps(payload).encode()
                ts, sig = sign_body(key_record.secret_key.encode(), body)
                try:
                    requests.post(
                        ps.webhook_url,
                        data=body,
                        headers={
                            "Content-Type": "application/json",
                            "X-Paycrypt-Key": key_record.key,
                            "X-Paycrypt-Timestamp": ts,
                            "X-Paycrypt-Signature": sig,
                        },
                        timeout=5,
                    )
                except Exception:
                    pass
        return redirect(ps.success_url)

    return render_template(
        "checkout.html",
        session=ps,
        fiat_amount=fiat_amount,
        selected_coin=selected_coin,
        selected_network=selected_network,
        crypto_amount=crypto_amount,
        deposit_address=deposit_address,
        qr_code=qr_code,
        seconds_left=seconds_left
    )
