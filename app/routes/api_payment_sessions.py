from flask import Blueprint, request, jsonify, current_app
from app.security.signing import verify_hmac
from app.models.payment_session import PaymentSession
from app.models.api_key import ClientApiKey
import json, time

payment_sessions_api = Blueprint("payment_sessions_api", __name__, url_prefix="/api/v1")

@payment_sessions_api.route("/payment_sessions", methods=["POST"]) 
def create_payment_session():
    raw = request.get_data() or b"{}"
    ts = request.headers.get("X-Paycrypt-Timestamp", "")
    sig = request.headers.get("X-Paycrypt-Signature", "")
    key = request.headers.get("X-Paycrypt-Key", "")

    key_record: ClientApiKey = ClientApiKey.query.filter_by(key=key, is_active=True).first()
    if not key_record or not key_record.secret_key:
        return jsonify({"error": "invalid key"}), 401

    # Optional: basic IP allowlist check
    if key_record.allowed_ips and request.remote_addr not in (key_record.allowed_ips or []):
        return jsonify({"error": "ip_not_allowed"}), 403

    verify_hmac(key_record.secret_key.encode(), raw, ts, sig)

    data = json.loads(raw.decode() or "{}")
    required = ["order_id", "amount", "currency", "success_url", "cancel_url", "webhook_url"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": "missing fields", "fields": missing}), 400

    ps = PaymentSession.create_from_request(data, client_id=key_record.client_id)
    checkout_host = (current_app.config.get("CHECKOUT_HOST") or request.host_url.rstrip("/"))
    checkout_url = f"{checkout_host}/checkout/{ps.public_id}"
    return jsonify({
        "id": ps.public_id,
        "status": ps.status,
        "checkout_url": checkout_url,
        "expires_at": int(time.time()) + 1800
    }), 201

@payment_sessions_api.route("/payment_sessions/<ps_id>", methods=["GET"]) 
def get_payment_session(ps_id):
    ps = PaymentSession.query.filter_by(public_id=ps_id).first()
    if not ps:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": ps.public_id,
        "status": ps.status,
        "order_id": ps.order_id,
        "amount": float(ps.amount),
        "currency": ps.currency,
    "metadata": ps.meta,
        "expires_at": int(ps.expires_at.timestamp()) if ps.expires_at else None
    })
