from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

from flask_babel import Babel
babel = Babel()

@babel.localeselector

def get_locale():
    from flask import session
    return session.get('lang', 'en')

# Export get_locale for import elsewhere
__all__ = ['db', 'login_manager', 'babel', 'get_locale']
