from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import os


# Load environment variables
load_dotenv()


from app.extensions import db, login_manager, cache
csrf = CSRFProtect()

def get_route_names():
    from flask import current_app
    return [rule.endpoint.split('.')[-1] for rule in current_app.url_map.iter_rules()]

def create_app():
    app = Flask(__name__)
    # configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-default-secret')
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise RuntimeError('DATABASE_URL environment variable must be set for production.')
    # Normalize legacy Postgres URL scheme for SQLAlchemy 2.x
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Improve DB connection resilience in production
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        # recycle slightly below common 300s idle timeouts on some hosts
        'pool_recycle': int(os.getenv('SQLALCHEMY_POOL_RECYCLE', '280')),
        'pool_size': int(os.getenv('SQLALCHEMY_POOL_SIZE', '5')),
        'max_overflow': int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', '10')),
    }

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # For development - disable CSRF for API testing
    app.config['WTF_CSRF_ENABLED'] = False
    csrf.init_app(app)
    
    # Initialize Babel
    from app.extensions import babel
    babel.init_app(app)
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'

    # Migrate setup
    from flask_migrate import Migrate
    migrate = Migrate(app, db)


    # Flask-Login user loader for both Client and User
    from app.models import Client, User
    @login_manager.user_loader
    def load_user(user_id):
        # Check if user_id contains type prefix
        if isinstance(user_id, str):
            if user_id.startswith('user_'):
                # Load as User
                actual_id = int(user_id.replace('user_', ''))
                return User.query.get(actual_id)
            elif user_id.startswith('client_'):
                # Load as Client
                actual_id = int(user_id.replace('client_', ''))
                return Client.query.get(actual_id)
        
        # Fallback: try to load as User first (for admin)
        user = User.query.get(int(user_id))
        if user:
            return user
        # If not found as User, try as Client
        return Client.query.get(int(user_id))

    # Custom unauthorized handler for Flask-Login
    from flask import redirect, request, url_for
    @login_manager.unauthorized_handler
    def custom_unauthorized():
        next_url = request.url
        # If accessing admin route, redirect to admin login
        if request.path.startswith('/admin120724'):
            return redirect(url_for('auth.admin_login', next=next_url))
        # Otherwise, redirect to client login
        return redirect(url_for('auth.login', next=next_url))
    login_manager.login_message_category = 'info'

    # Register custom filters
    from app.utils.filters import escapejs
    app.jinja_env.filters['escapejs'] = escapejs
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.client import client_bp
    from app.routes.admin import admin_bp
    from app.routes.main import main_bp, api_bp
    from app.routes.withdrawal_admin import withdrawal_admin
    from app.routes.api_v1 import api_v1
    from app.webhooks import webhooks
    from app.routes.tools import tools_bp
    from app.routes.api_payment_sessions import payment_sessions_api  # new
    from app.routes.checkout import checkout_bp  # new

    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(withdrawal_admin)
    app.register_blueprint(api_bp)
    app.register_blueprint(api_v1)
    app.register_blueprint(webhooks)
    app.register_blueprint(tools_bp)
    app.register_blueprint(payment_sessions_api)
    app.register_blueprint(checkout_bp)

    # Exempt JSON APIs from CSRF (they use Bearer auth, not cookies/forms)
    try:
        csrf.exempt(api_v1)
        csrf.exempt(api_bp)
        csrf.exempt(webhooks)
        csrf.exempt(payment_sessions_api)
    except Exception:
        pass

    # Inject get_locale into Jinja2 context
    from app.extensions.extensions import get_locale
    app.jinja_env.globals['get_locale'] = get_locale

    # Inject get_upgrade_package_name into Jinja2 context (if it exists)
    try:
        from app.utils.package_features import get_package_upgrade_recommendations as get_upgrade_package_name
        app.jinja_env.globals['get_upgrade_package_name'] = get_upgrade_package_name
    except ImportError:
        pass
    # Inject get_route_names into Jinja2 context
    app.jinja_env.globals['get_route_names'] = get_route_names
    
    # --- Disabled during migration: SmartBetslip client maintenance ---
    # @app.before_request
    # def ensure_flat_rate_clients_active():
    #     """Ensure flat-rate clients, especially SmartBetslip, remain active"""
    #     try:
    #         from app.decorators import ensure_smartbetslip_active
    #         ensure_smartbetslip_active()
    #     except Exception:
    #         pass  # Silently fail to avoid breaking requests
    
    app.config.setdefault('CHECKOUT_HOST', os.getenv('CHECKOUT_HOST', '').rstrip('/') or None)

    return app
# Placeholder for __init__.py
