from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
try:
    from flask_babel import Babel  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    class Babel:  # minimal shim to avoid hard dependency during migrations/tests
        def init_app(self, app):
            return None
from flask_caching import Cache

db = SQLAlchemy()
login_manager = LoginManager()
cache = Cache()


babel = Babel()


def get_locale():
    try:
        from flask import session  # lazy import to avoid early app context needs
        return session.get('lang', 'en')
    except Exception:
        return 'en'
