import hmac
import hashlib
import time
from werkzeug.exceptions import Forbidden


def verify_hmac(secret: bytes, raw_body: bytes, ts: str, sig: str, skew: int = 300):
    """Verify HMAC signature for API requests.

    expected = HMAC_SHA256(secret, f"{ts}." + raw_body)
    - Reject if timestamp skew > skew seconds
    - Constant-time comparison
    """
    if not ts or not sig:
        raise Forbidden("Missing signature headers")
    try:
        ts_i = int(ts)
    except Exception:
        raise Forbidden("Bad timestamp")
    now = int(time.time())
    if abs(now - ts_i) > skew:
        raise Forbidden("Stale request")
    message = (ts + ".").encode() + (raw_body or b"")
    expected = hmac.new(secret, msg=message, digestmod=hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        raise Forbidden("Bad signature")


def sign_body(secret: bytes, raw_body: bytes, ts: int | None = None) -> tuple[str, str]:
    """Helper to produce timestamp and hex signature for a payload."""
    ts_i = int(ts or time.time())
    message = (str(ts_i) + ".").encode() + (raw_body or b"")
    sig = hmac.new(secret, msg=message, digestmod=hashlib.sha256).hexdigest()
    return str(ts_i), sig
