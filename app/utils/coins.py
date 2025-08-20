"""
Coin utility functions for PayCrypt.
Handles coin validation, package limits, and display formatting.
"""
from functools import lru_cache
from flask import current_app, g, has_request_context

@lru_cache(maxsize=128)
def get_coin_display_name(coin_symbol):
    """Get the display name for a coin symbol."""
    if not coin_symbol:
        return ""
    return current_app.config.get('COIN_DISPLAY_NAMES', {}).get(coin_symbol.upper(), coin_symbol.upper())

def get_allowed_coins(package_slug):
    """
    Return allowed coin symbols based on client's package slug.
    
    Args:
        package_slug (str): The package slug (e.g., 'starter_flat_rate')
        
    Returns:
        list: List of allowed coin symbols
    """
    if not package_slug:
        return []
        
    limits = current_app.config.get('PACKAGE_COIN_LIMITS', {})
    coin_list = current_app.config.get('COIN_LIST', [])
    
    # Default to starter plan if package not found
    limit = limits.get(package_slug, limits.get('starter_flat_rate', 15))
    return coin_list[:min(limit, len(coin_list))]

def is_coin_allowed(client, coin_symbol):
    """
    Validate if the given coin is allowed for the client.
    
    Args:
        client: The client object with package information
        coin_symbol (str): The coin symbol to check
        
    Returns:
        bool: True if coin is allowed, False otherwise
    """
    if not client or not client.package or not coin_symbol:
        return False
        
    allowed = get_allowed_coins(client.package.slug)
    return coin_symbol.upper() in [c.upper() for c in allowed]

def get_coin_icon(coin_symbol):
    """
    Get the CSS class for a coin icon.
    
    Args:
        coin_symbol (str): The coin symbol
        
    Returns:
        str: CSS class for the coin icon
    """
    if not coin_symbol:
        return "crypto-icon crypto-unknown"
    return f"crypto-icon crypto-{coin_symbol.lower()}"

def get_client_coins(client):
    """
    Get the list of coins available to a client based on their package.
    
    Args:
        client: The client object with package information
        
    Returns:
        list: List of dicts with coin info: [{'symbol': 'BTC', 'name': 'Bitcoin'}, ...]
    """
    if not client or not client.package:
        return []
        
    symbols = get_allowed_coins(client.package.slug)
    return [
        {
            'symbol': symbol,
            'name': get_coin_display_name(symbol),
            'icon': get_coin_icon(symbol)
        }
        for symbol in symbols
    ]

# Context processor to make coins available in templates
def coins_context_processor():
    """Make coin-related functions available in all templates."""
    if not has_request_context() or not hasattr(g, 'user') or not hasattr(g.user, 'client'):
        return {}
        
    return {
        'allowed_coins': get_client_coins(g.user.client),
        'get_coin_display_name': get_coin_display_name,
        'get_coin_icon': get_coin_icon
    }
