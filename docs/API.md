# PayCrypt API

This guide covers the HMAC-signed Payment Session API, hosted checkout, and webhooks.

## Security headers
- X-Paycrypt-Key: your API key
- X-Paycrypt-Timestamp: unix seconds (UTC)
- X-Paycrypt-Signature: hex sha256 HMAC of "<ts>.<raw_body>" using your secret
  - Reject if |now - ts| > 300s

## Create a payment session
POST /api/v1/payment_sessions

Body:
{
  "order_id": "ORD-123",
  "amount": "49.00",
  "currency": "USD",
  "customer": {"email": "buyer@example.com"},
  "metadata": {"source": "merchant"},
  "success_url": "https://merchant.tld/success?oid=ORD-123",
  "cancel_url": "https://merchant.tld/cancel?oid=ORD-123",
  "webhook_url": "https://merchant.tld/api/paycrypt/webhook"
}

Response 201:
{
  "id": "ps_abcd1234ef56",
  "status": "created",
  "checkout_url": "https://paycrypt.tld/checkout/ps_abcd1234ef56",
  "expires_at": 1723650000
}

### curl example (Windows PowerShell)
$body = '{"order_id":"ORD-123","amount":"49.00","currency":"USD","customer":{"email":"buyer@example.com"},"metadata":{"source":"merchant"},"success_url":"https://merchant.tld/success?oid=ORD-123","cancel_url":"https://merchant.tld/cancel?oid=ORD-123","webhook_url":"https://merchant.tld/api/paycrypt/webhook"}'
$ts = [int][double]::Parse((Get-Date -Date (Get-Date).ToUniversalTime() -UFormat %s))
$secret = "YOUR_SECRET"
$hmac = New-Object System.Security.Cryptography.HMACSHA256 ([Text.Encoding]::UTF8.GetBytes($secret))
$bytes = [Text.Encoding]::UTF8.GetBytes("$ts." + $body)
$sig = ($hmac.ComputeHash($bytes) | ForEach-Object ToString x2) -join ''
Invoke-RestMethod -Method Post -Uri "https://your-host/api/v1/payment_sessions" -Headers @{
  'X-Paycrypt-Key'='YOUR_KEY'; 'X-Paycrypt-Timestamp'=$ts; 'X-Paycrypt-Signature'=$sig
} -ContentType 'application/json' -Body $body

### Node.js example
const crypto = require('crypto');
async function createSession() {
  const body = JSON.stringify({
    order_id: 'ORD-123', amount: '49.00', currency: 'USD',
    customer: { email: 'buyer@example.com' }, metadata: { source: 'merchant' },
    success_url: 'https://merchant.tld/success?oid=ORD-123',
    cancel_url: 'https://merchant.tld/cancel?oid=ORD-123',
    webhook_url: 'https://merchant.tld/api/paycrypt/webhook'
  });
  const ts = Math.floor(Date.now()/1000).toString();
  const sig = crypto.createHmac('sha256', process.env.PAYCRYPT_SECRET).update(`${ts}.${body}`).digest('hex');
  const res = await fetch('https://your-host/api/v1/payment_sessions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Paycrypt-Key': process.env.PAYCRYPT_KEY,
      'X-Paycrypt-Timestamp': ts,
      'X-Paycrypt-Signature': sig,
    },
    body,
  });
  console.log(await res.json());
}

### Django webhook verification
import hmac, hashlib, time
from django.http import HttpResponse, JsonResponse

def paycrypt_webhook(request):
    key = request.headers.get('X-Paycrypt-Key')
    ts = request.headers.get('X-Paycrypt-Timestamp') or ''
    sig = request.headers.get('X-Paycrypt-Signature') or ''
    raw = request.body or b''

    # optional: check expected key
    if key != 'YOUR_KEY':
        return HttpResponse(status=401)

    try:
        ts_int = int(ts)
        if abs(int(time.time()) - ts_int) > 300:
            return HttpResponse(status=400)
    except Exception:
        return HttpResponse(status=400)

    expected = hmac.new(b'YOUR_SECRET', f"{ts}.{raw.decode()}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return HttpResponse(status=401)

    # process event JSON
    import json
    evt = json.loads(raw.decode() or '{}')
    # ... handle types like payment.succeeded

    return JsonResponse({'ok': True})
