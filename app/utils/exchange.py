from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timedelta
from functools import lru_cache
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional during migrations/tests
    class requests:  # minimal shim
        @staticmethod
        def get(*args, **kwargs):
            raise RuntimeError("requests not available in this environment")
from flask import current_app
from app.extensions import cache
from .crypto_config import SUPPORTED_CRYPTOCURRENCIES, get_cryptocurrency_info

# Enhanced default exchange rates with multiple cryptocurrencies
DEFAULT_RATES = {}

# Build default rates from crypto config
for symbol, info in SUPPORTED_CRYPTOCURRENCIES.items():
    DEFAULT_RATES[symbol] = {
        'USD': info['default_rate_usd'],
        'EUR': info['default_rate_usd'] * Decimal('0.92'),  # Approximate EUR rate
        'GBP': info['default_rate_usd'] * Decimal('0.79'),  # Approximate GBP rate
        'TRY': info['default_rate_usd'] * Decimal('28.5'),  # Approximate TRY rate
    }

def get_exchange_rate(crypto_currency, fiat_currency='USD'):
    """
    Get the current exchange rate from crypto to fiat.
    
    Args:
        crypto_currency (str): The cryptocurrency code (e.g., 'BTC', 'ETH')
        fiat_currency (str): The fiat currency code (default: 'USD')
        
    Returns:
        Decimal: The exchange rate (1 crypto = X fiat)
    """
    crypto_currency = crypto_currency.upper()
    fiat_currency = fiat_currency.upper()
    
    # Check if cryptocurrency is supported
    if crypto_currency not in SUPPORTED_CRYPTOCURRENCIES:
        current_app.logger.error(f"Unsupported cryptocurrency: {crypto_currency}")
        return None
    
    # Try to fetch live rate first
    rate = _fetch_cached_rate(crypto_currency, fiat_currency)
    
    # Fall back to default rates
    if rate is None and crypto_currency in DEFAULT_RATES and fiat_currency in DEFAULT_RATES[crypto_currency]:
        rate = DEFAULT_RATES[crypto_currency][fiat_currency]
        current_app.logger.warning(
            f"Using default rate for {crypto_currency} -> {fiat_currency}: {rate}"
        )
    
    if rate is None:
        current_app.logger.error(
            f"No exchange rate available for {crypto_currency} -> {fiat_currency}"
        )
        return None
    
    return rate

def convert_fiat_to_crypto(fiat_amount, fiat_currency, crypto_currency):
    """
    Convert fiat amount to crypto amount using the current exchange rate.
    
    Args:
        fiat_amount (Decimal): Amount in fiat currency
        fiat_currency (str): Fiat currency code (e.g., 'USD', 'EUR')
        crypto_currency (str): Cryptocurrency code (e.g., 'BTC', 'ETH')
        
    Returns:
        tuple: (crypto_amount, exchange_rate) or (None, None) if conversion fails
    """
    if not fiat_amount or fiat_amount <= 0:
        return None, None
        
    rate = get_exchange_rate(crypto_currency, fiat_currency)
    if not rate:
        return None, None
    
    # Get cryptocurrency info for proper decimal formatting
    crypto_info = get_cryptocurrency_info(crypto_currency)
    decimal_places = crypto_info['decimal_places'] if crypto_info else 8
    
    # Calculate crypto amount: fiat_amount / rate
    crypto_amount = (Decimal(str(fiat_amount)) / rate).quantize(
        Decimal('0.' + '0' * decimal_places),
        rounding=ROUND_DOWN
    )
    
    return crypto_amount, rate

def get_supported_cryptocurrencies():
    """Get list of all supported cryptocurrencies"""
    return list(SUPPORTED_CRYPTOCURRENCIES.keys())

def get_popular_cryptocurrencies():
    """Get list of popular cryptocurrencies"""
    return [symbol for symbol, info in SUPPORTED_CRYPTOCURRENCIES.items() if info.get('popular', False)]

def format_crypto_amount(amount, currency):
    """Format a crypto amount with appropriate decimal places"""
    if not amount:
        return f"0 {currency}"
    
    # Use crypto config for proper formatting
    crypto_info = get_cryptocurrency_info(currency)
    if crypto_info:
        decimal_places = crypto_info['decimal_places']
        return f"{amount:.{decimal_places}f} {currency}"
    
    # Default formatting for unknown currencies
    return f"{amount:.8f} {currency}"

def format_fiat_amount(amount, currency):
    """Format a fiat amount with appropriate decimal places"""
    if not amount:
        return f"0 {currency}"
    return f"{amount:,.2f} {currency}"

@lru_cache(maxsize=128)
def _fetch_cached_rate(crypto_currency, fiat_currency):
    """
    Fetch exchange rate with caching.
    This is a placeholder that would be replaced with actual API calls.
    """
    # In a real implementation, you would call an exchange API here
    # For example, using CoinGecko, CoinMarketCap, or a crypto exchange API
    
    # Example with CoinGecko (uncomment and implement as needed):
    """
    try:
        crypto_info = get_cryptocurrency_info(crypto_currency)
        if not crypto_info:
            return None
            
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': crypto_info['api_id'],
            'vs_currencies': fiat_currency.lower(),
            'precision': 8
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        rate = Decimal(str(data[crypto_info['api_id']][fiat_currency.lower()]))
        return rate
        
    except Exception as e:
        current_app.logger.error(f"Error fetching exchange rate: {str(e)}")
        return None
    """
    
    # For now, return None to use the default rates
    return None

# Cache exchange rates for 5 minutes
@cache.memoize(timeout=300)
def get_cached_rate(crypto_currency, fiat_currency):
    """
    Get a cached exchange rate with a 5-minute expiry.
    Uses Flask-Caching for distributed caching.
    """
    return _fetch_cached_rate(crypto_currency, fiat_currency)

# Alias for backward compatibility
get_exchange_rate_cached = get_cached_rate
