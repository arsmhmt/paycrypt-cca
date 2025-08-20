"""
Internationalization utilities for the PayCrypt application.
Handles language detection, switching, and localization functions.
"""

from flask import request, session, current_app
from flask_babel import get_locale
import os


def get_supported_languages():
    """Get the list of supported languages from config."""
    return current_app.config.get('LANGUAGES', {'en': 'English'})


def get_current_language():
    """Get the current language code."""
    return str(get_locale())


def get_locale_selector():
    """
    Select the best language based on user preference, session, or browser.
    This function is used by Flask-Babel to determine the locale.
    """
    # 1. Check if language is set in session (user manually selected)
    if 'language' in session:
        language = session['language']
        if language in current_app.config['LANGUAGES']:
            return language
    
    # 2. Check Accept-Language header from browser
    return request.accept_languages.best_match(
        current_app.config['LANGUAGES'].keys()
    ) or current_app.config['BABEL_DEFAULT_LOCALE']


def set_language(language_code):
    """Set the language in the session."""
    if language_code in current_app.config['LANGUAGES']:
        session['language'] = language_code
        return True
    return False


def get_language_name(language_code):
    """Get the display name for a language code."""
    return current_app.config['LANGUAGES'].get(language_code, language_code)


def get_timezone():
    """Get the timezone for the current user."""
    # For now, return UTC. In the future, this could be user-specific
    return current_app.config.get('BABEL_DEFAULT_TIMEZONE', 'UTC')


def is_rtl_language(language_code=None):
    """Check if the given language (or current language) is right-to-left."""
    if language_code is None:
        language_code = get_current_language()
    
    # RTL languages list (can be extended)
    rtl_languages = ['ar', 'he', 'fa', 'ur']
    return language_code in rtl_languages


def format_currency(amount, currency='USD', language_code=None):
    """Format currency for the given language."""
    if language_code is None:
        language_code = get_current_language()
    
    # Basic currency formatting - can be enhanced with babel.numbers
    if currency in ['BTC', 'ETH', 'LTC']:
        # Crypto currencies - show more decimal places
        return f"{amount:.8f} {currency}"
    else:
        # Fiat currencies
        return f"{amount:.2f} {currency}"


def get_flag_emoji(language_code):
    """Get flag emoji for language code."""
    flag_map = {
        'en': '🇺🇸',  # or 🇬🇧 for UK
        'tr': '🇹🇷',
        'ru': '🇷🇺',
        'es': '🇪🇸',
        'fr': '🇫🇷',
        'de': '🇩🇪',
        'ar': '🇸🇦',
        'zh': '🇨🇳',
        'ja': '🇯🇵',
        'ko': '🇰🇷'
    }
    return flag_map.get(language_code, '🌐')
