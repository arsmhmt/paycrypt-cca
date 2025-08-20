from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app
from sqlalchemy import func
from datetime import datetime, timedelta
from app.forms_withdrawal import WithdrawalRequestForm
from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus
from flask_login import login_user, logout_user, login_required, current_user
from app.models import Client
from app.models.user import User
from app import db
from werkzeug.security import check_password_hash
from app.decorators import client_required
from app.models.api_key import ClientApiKey, ApiKeyScope

client_bp = Blueprint("client", __name__, url_prefix="/client")

@client_bp.context_processor
def inject_client_context():
    """Make client data available to all client templates"""
    if current_user.is_authenticated:
        if isinstance(current_user, User) and current_user.client:
            # User with linked client
            return {'client': current_user.client}
        elif isinstance(current_user, Client):
            # Direct client login
            return {'client': current_user}
    return {}

# --- Payments Page (stub) ---
@client_bp.route('/payments')
@login_required
def payments():
    # TODO: Implement payments logic
    class PaymentStub:
        def __init__(self):
            self.items = []
            self.pages = 1
            self.page = 1
        def iter_pages(self):
            return [1]
    payments = PaymentStub()
    return render_template('client/payments.html', client=current_user, payments=payments)

# --- Withdraw Page (stub) ---
@client_bp.route('/withdraw')
@login_required
@client_required
def withdraw():
    # TODO: Implement withdraw logic
    return render_template('client/withdraw_simple.html')

# --- Payment History Page (stub) ---
@client_bp.route('/payment-history')
@login_required
@client_required
def payment_history():
    # TODO: Implement payment history logic
    return render_template('client/payment_history.html')

# --- Support Page (stub) ---
@client_bp.route('/support')
@login_required
@client_required
def support():
    # TODO: Implement support logic
    return render_template('client/support.html')

# --- Profile Page (stub) ---
@client_bp.route('/profile')
@login_required
@client_required
def profile():
    # TODO: Implement profile logic
    return render_template('client/profile.html', client=current_user)

# --- API Management (Client) ---
@client_bp.route('/api', methods=['GET'], endpoint='api_management')
@login_required
@client_required
def api_management():
    # Resolve client record for current user
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))

    keys = ClientApiKey.query.filter_by(client_id=client_data.id).order_by(ClientApiKey.created_at.desc()).all()
    # Expose scopes grouped by type for UI help
    flat_scopes = [s.value for s in ApiKeyScope if s.value.startswith('flat_rate:')]
    commission_scopes = [s.value for s in ApiKeyScope if s.value.startswith('commission:')]
    return render_template('client/api_management.html', client=client_data, api_keys=keys,
                           flat_scopes=flat_scopes, commission_scopes=commission_scopes)


@client_bp.route('/api/keys/create', methods=['POST'], endpoint='create_api_key_management')
@login_required
@client_required
def create_api_key_management():
    # Resolve client
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))

    # Optional: parse permissions selection from form
    requested_perms = request.form.getlist('permissions') or []

    # Create an API key tailored to client type
    api_key = ClientApiKey.create_for_client_by_type(
        client=client_data,
        name=request.form.get('name', 'Default API Key'),
        permissions=requested_perms or None,
        rate_limit=None,
        expires_at=None,
    )

    # Persist (create_for_client_by_type does not commit)
    db.session.add(api_key)
    db.session.commit()

    # We return the key and secret one time via flash message and redirect to management page
    from flask_babel import _
    flash(_(f"API key created. Copy now: Key={api_key.key} · Secret={api_key.secret_key}"), 'success')
    return redirect(url_for('client.api_management'))


@client_bp.route('/api/keys/<int:key_id>/deactivate', methods=['POST'])
@login_required
@client_required
def deactivate_api_key(key_id: int):
    # Ensure ownership
    client_id = getattr(current_user, 'id', None) if current_user.__class__.__name__ == 'Client' else getattr(getattr(current_user, 'client', None), 'id', None)
    key = ClientApiKey.query.filter_by(id=key_id, client_id=client_id).first()
    if not key:
        from flask_babel import _
        flash(_("API key not found"), 'danger')
        return redirect(url_for('client.api_management'))
    key.is_active = False
    db.session.commit()
    from flask_babel import _
    flash(_("API key deactivated"), 'info')
    return redirect(url_for('client.api_management'))

# --- Withdrawal Analytics (stub) ---
@client_bp.route('/withdrawal-analytics')
@login_required
@client_required
def withdrawal_analytics():
    from app.models import Payment, WithdrawalRequest, Transaction
    from app.models.enums import PaymentStatus, WithdrawalStatus
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    import calendar
    
    # Get client data properly
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
        client_id = current_user.client.id
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
        client_id = current_user.id
    
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))
    
    # Date filters
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    year_start = datetime(end_date.year, 1, 1)
    
    # === PAYMENT ANALYTICS ===
    # Total payments received
    total_payments = db.session.query(func.sum(Payment.fiat_amount)).filter(
        Payment.client_id == client_id,
        Payment.status == PaymentStatus.COMPLETED
    ).scalar() or 0
    
    # Payments in the last 30 days
    recent_payments = db.session.query(func.sum(Payment.fiat_amount)).filter(
        Payment.client_id == client_id,
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at >= start_date
    ).scalar() or 0
    
    # Payment count
    payment_count = Payment.query.filter(
        Payment.client_id == client_id,
        Payment.status == PaymentStatus.COMPLETED
    ).count()
    
    # === WITHDRAWAL ANALYTICS ===
    # Total withdrawals processed
    total_withdrawals = db.session.query(func.sum(WithdrawalRequest.net_amount)).filter(
        WithdrawalRequest.client_id == client_id,
        WithdrawalRequest.status == WithdrawalStatus.COMPLETED
    ).scalar() or 0
    
    # Pending withdrawals
    pending_withdrawals = db.session.query(func.sum(WithdrawalRequest.amount)).filter(
        WithdrawalRequest.client_id == client_id,
        WithdrawalRequest.status == WithdrawalStatus.PENDING
    ).scalar() or 0
    
    # Withdrawal count
    withdrawal_count = WithdrawalRequest.query.filter(
        WithdrawalRequest.client_id == client_id
    ).count()
    
    # === MONTHLY BREAKDOWN ===
    # Monthly payment data (last 12 months)
    monthly_payments = db.session.query(
        extract('year', Payment.created_at).label('year'),
        extract('month', Payment.created_at).label('month'),
        func.sum(Payment.fiat_amount).label('total'),
        func.count(Payment.id).label('count')
    ).filter(
        Payment.client_id == client_id,
        Payment.status == PaymentStatus.COMPLETED,
        Payment.created_at >= datetime(end_date.year - 1, end_date.month, 1)
    ).group_by(
        extract('year', Payment.created_at),
        extract('month', Payment.created_at)
    ).order_by(
        extract('year', Payment.created_at),
        extract('month', Payment.created_at)
    ).all()
    
    # Monthly withdrawal data
    monthly_withdrawals = db.session.query(
        extract('year', WithdrawalRequest.created_at).label('year'),
        extract('month', WithdrawalRequest.created_at).label('month'),
        func.sum(WithdrawalRequest.net_amount).label('total'),
        func.count(WithdrawalRequest.id).label('count')
    ).filter(
        WithdrawalRequest.client_id == client_id,
        WithdrawalRequest.status == WithdrawalStatus.COMPLETED,
        WithdrawalRequest.created_at >= datetime(end_date.year - 1, end_date.month, 1)
    ).group_by(
        extract('year', WithdrawalRequest.created_at),
        extract('month', WithdrawalRequest.created_at)
    ).order_by(
        extract('year', WithdrawalRequest.created_at),
        extract('month', WithdrawalRequest.created_at)
    ).all()
    
    # === CURRENCY BREAKDOWN ===
    # Payment by currency
    payment_by_currency = db.session.query(
        Payment.crypto_currency.label('currency'),
        func.sum(Payment.fiat_amount).label('fiat_total'),
        func.sum(Payment.crypto_amount).label('crypto_total'),
        func.count(Payment.id).label('count')
    ).filter(
        Payment.client_id == client_id,
        Payment.status == PaymentStatus.COMPLETED
    ).group_by(Payment.crypto_currency).all()
    
    # Withdrawal by currency
    withdrawal_by_currency = db.session.query(
        WithdrawalRequest.currency.label('currency'),
        func.sum(WithdrawalRequest.net_amount).label('total'),
        func.count(WithdrawalRequest.id).label('count')
    ).filter(
        WithdrawalRequest.client_id == client_id,
        WithdrawalRequest.status == WithdrawalStatus.COMPLETED
    ).group_by(WithdrawalRequest.currency).all()
    
    # === RECENT TRANSACTIONS ===
    # Recent payments (last 10)
    recent_payments_list = Payment.query.filter(
        Payment.client_id == client_id
    ).order_by(Payment.created_at.desc()).limit(10).all()
    
    # Recent withdrawals (last 10)
    recent_withdrawals_list = WithdrawalRequest.query.filter(
        WithdrawalRequest.client_id == client_id
    ).order_by(WithdrawalRequest.created_at.desc()).limit(10).all()
    
    # === BALANCE INFO ===
    current_balance = client_data.balance or 0
    
    # Net profit (payments - withdrawals)
    net_profit = float(total_payments or 0) - float(total_withdrawals or 0)
    
    # Package the data for the template
    analytics_data = {
        'summary': {
            'total_payments': float(total_payments or 0),
            'recent_payments': float(recent_payments or 0),
            'payment_count': payment_count,
            'total_withdrawals': float(total_withdrawals or 0),
            'pending_withdrawals': float(pending_withdrawals or 0),
            'withdrawal_count': withdrawal_count,
            'current_balance': float(current_balance),
            'net_profit': net_profit
        },
        'monthly_payments': monthly_payments,
        'monthly_withdrawals': monthly_withdrawals,
        'payment_by_currency': payment_by_currency,
        'withdrawal_by_currency': withdrawal_by_currency,
        'recent_payments': recent_payments_list,
        'recent_withdrawals': recent_withdrawals_list
    }
    
    return render_template('client/withdrawal_analytics.html', 
                         client=client_data,
                         analytics=analytics_data)

# --- Invoices Page ---
@client_bp.route("/invoices")
@login_required
@client_required
def invoices():
    return render_template("client/invoices.html")


# --- Documents Page ---
@client_bp.route("/documents")
@login_required
@client_required
def documents():
    return render_template("client/documents.html")


# --- Login ---
@client_bp.route("/login", methods=["GET", "POST"])
def client_login():
    if current_user.is_authenticated:
        return redirect(url_for("client.client_dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        client = Client.query.filter_by(username=username).first()
        if client and client.check_password(password):
            login_user(client)
            return redirect(url_for("client.client_dashboard"))
        from flask_babel import _
        flash(_("Invalid credentials"), "danger")

    return render_template("auth/client_login.html")


# --- Logout ---
@client_bp.route("/logout", endpoint="logout")
@login_required
def client_logout():
    logout_user()
    return redirect(url_for("client.client_login"))


# --- Dashboard ---
@client_bp.route("/dashboard")
@login_required
def client_dashboard():
    # Check if user has client role or is a Client instance
    is_client = False
    client_data = None
    
    if isinstance(current_user, User) and current_user.client:
        # User with linked client
        is_client = True
        client_data = current_user.client
    elif isinstance(current_user, Client):
        # Direct Client instance
        is_client = True
        client_data = current_user
    
    if not is_client or not client_data:
        from flask_babel import _
        flash(_("Unauthorized access - Client access required"), "danger")
        return redirect(url_for("auth.login"))
    
    # The template will get proper client data from context processor
    return render_template("client/dashboard.html")


# --- Wallet/API Settings ---
@client_bp.route("/settings", methods=["GET", "POST"])
@login_required
@client_required
@client_bp.route("/settings", methods=["GET", "POST"], endpoint="settings")
def client_settings():
    # Get client data properly for both User and Client objects
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        current_user.wallet_address = request.form["wallet_address"]
        current_user.api_key = request.form["api_key"]
        current_user.api_secret = request.form["api_secret"]
        db.session.commit()
        from flask_babel import _
        flash(_("Settings updated"), "success")
        return redirect(url_for("client.client_settings"))

    return render_template("client/settings.html")

# --- Notification Preferences ---
@client_bp.route("/notification-preferences", methods=["GET", "POST"])
@login_required
@client_required
def notification_preferences():
    # Add logic to fetch and update notification preferences
    return render_template("client/notification_preferences.html")

# --- Wallet Configure Page ---
@client_bp.route("/wallet-configure")
@login_required
@client_required
def wallet_configure():
    # Get client data properly
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))
    
    # Get client wallets from database
    from app.models import ClientWallet
    wallets = ClientWallet.query.filter_by(client_id=client_data.id).all()
    
    # Get client type for wallet features
    client_type = 'flat_rate' if client_data.package and 'flat' in client_data.package.name.lower() else 'commission'
    
    return render_template("client/wallet_configure.html", 
                         client=client_data,
                         wallets=wallets,
                         client_type=client_type)

# --- Create Wallet Configuration ---
@client_bp.route("/wallet-configure/create", methods=["POST"])
@login_required
@client_required
def create_wallet():
    # Get client data properly
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))
    
    from app.models import ClientWallet, WalletType, WalletStatus
    
    wallet_name = request.form.get('wallet_name', 'Default Wallet')
    wallet_type = request.form.get('wallet_type', 'CUSTOM_MANUAL')
    supported_currencies = request.form.getlist('currencies') or ['USDT', 'BTC', 'ETH']
    
    # Convert string to enum
    try:
        wallet_type_enum = WalletType(wallet_type)
    except ValueError:
        wallet_type_enum = WalletType.CUSTOM_MANUAL
    
    new_wallet = ClientWallet(
        client_id=client_data.id,
        wallet_name=wallet_name,
        wallet_type=wallet_type_enum,
        status=WalletStatus.PENDING_VERIFICATION,
        supported_currencies=supported_currencies,
        settings={}
    )
    
    db.session.add(new_wallet)
    db.session.commit()
    
    from flask_babel import _
    flash(_(f"Wallet '{wallet_name}' created successfully!"), "success")
    
    return redirect(url_for("client.wallet_configure"))

# Alias for backward compatibility with templates
@client_bp.route("/wallets")
@login_required
@client_required  
def wallets():
    # Redirect to wallet_configure for now
    return redirect(url_for('client.wallet_configure'))


# --- Withdrawal Requests Page ---
@client_bp.route("/withdrawal-requests")
@login_required
@client_required
def withdrawal_requests():
    # Get client data properly
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))

    status = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    query = WithdrawalRequest.query.filter_by(client_id=client_data.id)
    if status and status != 'all':
        query = query.filter(WithdrawalRequest.status == WithdrawalStatus[status.upper()])
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(WithdrawalRequest.created_at >= start)
        except Exception:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(WithdrawalRequest.created_at < end)
        except Exception:
            pass
    query = query.order_by(WithdrawalRequest.created_at.desc())
    withdrawal_requests = query.paginate(page=page, per_page=20)

    # Status counts for stat boxes
    status_counts = {
        'ALL': WithdrawalRequest.query.filter_by(client_id=current_user.id).count(),
        'PENDING': WithdrawalRequest.query.filter_by(client_id=current_user.id, status=WithdrawalStatus.PENDING).count(),
        'APPROVED': WithdrawalRequest.query.filter_by(client_id=current_user.id, status=WithdrawalStatus.APPROVED).count(),
        'COMPLETED': WithdrawalRequest.query.filter_by(client_id=current_user.id, status=WithdrawalStatus.COMPLETED).count(),
        'REJECTED': WithdrawalRequest.query.filter_by(client_id=current_user.id, status=WithdrawalStatus.REJECTED).count(),
    }

    return render_template(
        "client/withdrawal_requests.html",
        client=current_user,
        withdrawal_requests=withdrawal_requests,
        status=status,
        status_counts=status_counts
    )

# --- Create Withdrawal Request ---
@client_bp.route("/withdrawal-requests/create", methods=["GET", "POST"])
@login_required
@client_required
def create_withdrawal_request():
    # Get client data properly
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))

    form = WithdrawalRequestForm()
    # Populate currency choices dynamically (example: USDT, BTC, ETH)
    form.currency.choices = [(c, c) for c in ["USDT", "BTC", "ETH"]]

    if form.validate_on_submit():
        req = WithdrawalRequest(
            client_id=client_data.id,
            currency=form.currency.data,
            amount=form.amount.data,
            user_wallet_address=form.user_wallet_address.data,
            memo=form.memo.data,
            note=form.note.data,
            status=WithdrawalStatus.PENDING,
            created_at=datetime.utcnow()
        )
        from app import db
        db.session.add(req)
        db.session.commit()
        from flask_babel import _
        flash(_("Withdrawal request submitted and pending admin approval."), "success")
        return redirect(url_for("client.withdrawal_requests"))

    return render_template(
        "client/create_withdrawal_request.html",
        form=form
    )

# --- API Keys Page ---
@client_bp.route("/api-keys", endpoint="api_keys")
@login_required
@client_required
def api_keys():
    # Get client data properly
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))
    
    # Get client API keys from database
    from app.models import ClientApiKey
    api_keys = ClientApiKey.query.filter_by(client_id=client_data.id).all()
    
    # Check if client has main API key in client table
    main_api_key = client_data.api_key if hasattr(client_data, 'api_key') else None
    
    # Get client type for permissions display
    client_type = 'flat_rate' if client_data.package and 'flat' in client_data.package.name.lower() else 'commission'
    
    # Create key stats (placeholder for now - can be enhanced with actual usage stats)
    key_stats = {}
    for key in api_keys:
        key_stats[key.id] = {
            'requests_count': 0,  # TODO: Implement actual API request tracking
            'last_used': None,    # TODO: Implement last used tracking
            'rate_limit_hits': 0  # TODO: Implement rate limit tracking
        }
    
    return render_template("client/api_keys.html", 
                         client=client_data,
                         api_keys=api_keys,
                         main_api_key=main_api_key,
                         client_type=client_type,
                         key_stats=key_stats)

# --- Create API Key ---
@client_bp.route("/api-keys/create", methods=["POST"])
@login_required
@client_required
def create_api_key():
    # Get client data properly
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))
    
    # Generate API key and secrets
    import secrets
    import hashlib
    from app.models import ClientApiKey
    
    key_name = request.form.get('name', 'Default API Key')
    api_key = f"pk_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    key_prefix = api_key[:8]
    
    # Generate secret key for signing requests
    secret_key = secrets.token_hex(32)
    
    # Generate webhook secret for webhook verification
    webhook_secret = secrets.token_hex(24)
    
    # Get client type for appropriate permissions
    client_type = 'flat_rate' if client_data.package and 'flat' in client_data.package.name.lower() else 'commission'
    
    # Default permissions based on client type
    default_permissions = []
    if client_type == 'flat_rate':
        default_permissions = [
            'flat_rate:payment:create',
            'flat_rate:payment:read', 
            'flat_rate:balance:read',
            'flat_rate:withdrawal:create',
            'flat_rate:webhook:manage'
        ]
    else:
        default_permissions = [
            'commission:payment:create',
            'commission:payment:read',
            'commission:balance:read'
        ]
    
    new_api_key = ClientApiKey(
        client_id=client_data.id,
        name=key_name,
        key=api_key,
        key_prefix=key_prefix,
        key_hash=key_hash,
        client_type=client_type,
        permissions=default_permissions,
        rate_limit=1000 if client_type == 'flat_rate' else 100,
        secret_key=secret_key,
        webhook_secret=webhook_secret
    )
    
    db.session.add(new_api_key)
    db.session.commit()
    
    from flask_babel import _
    flash(_(f"API Key '{key_name}' created successfully!"), "success")
    flash(_(f"Your API Key: {api_key} (Save this - it won't be shown again!)"), "info")
    
    return redirect(url_for("client.api_keys"))

# --- API Key Details with all credentials ---
@client_bp.route("/api-keys/<int:key_id>/details", methods=["GET"])
@login_required
@client_required
def api_key_details(key_id):
    # Get client data properly
    client_data = None
    if hasattr(current_user, 'client') and current_user.client:
        client_data = current_user.client
    elif current_user.__class__.__name__ == 'Client':
        client_data = current_user
    
    if not client_data:
        from flask_babel import _
        flash(_("Client data not found"), "danger")
        return redirect(url_for("auth.login"))
    
    # Get the specific API key
    from app.models import ClientApiKey
    api_key = ClientApiKey.query.filter_by(
        id=key_id, 
        client_id=client_data.id
    ).first()
    
    if not api_key:
        from flask_babel import _
        flash(_("API Key not found"), "danger")
        return redirect(url_for("client.api_keys"))
    
    # Get base URL from config or default
    base_url = current_app.config.get('PAYCRYPT_BASE_URL', 'https://api.paycrypt.online/v1')
    
    return render_template("client/api_key_credentials.html", 
                         client=client_data,
                         api_key=api_key,
                         base_url=base_url)

# --- API Documentation Page ---
@client_bp.route("/api-docs", endpoint="api_docs")
@login_required
@client_required
def api_docs():
    return render_template("client/api_docs.html")

# --- Pricing Page (stub) ---
@client_bp.route('/pricing')
def pricing():
    return render_template('pricing.html', client=current_user)
