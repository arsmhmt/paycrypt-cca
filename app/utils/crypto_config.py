"""
Supported Cryptocurrencies for Paycrypt Payment System
Configuration for all supported crypto payment options
"""

from decimal import Decimal

# Comprehensive list of supported cryptocurrencies
SUPPORTED_CRYPTOCURRENCIES = {
    # Major Cryptocurrencies
    'BTC': {
        'name': 'Bitcoin',
        'symbol': 'BTC',
        'decimal_places': 8,
        'network': 'Bitcoin',
        'default_rate_usd': Decimal('45000.00'),  # Fallback rate
        'api_id': 'bitcoin',  # For CoinGecko API
        'icon': 'bitcoin',
        'popular': True
    },
    'BTC-BLOCKCHAIN': {
        'name': 'Bitcoin (Blockchain)',
        'symbol': 'BTC',
        'decimal_places': 8,
        'network': 'Bitcoin Blockchain',
        'default_rate_usd': Decimal('45000.00'),
        'api_id': 'bitcoin',
        'icon': 'bitcoin',
        'popular': True,
        'description': 'Direct Bitcoin blockchain payments'
    },
    'ETH': {
        'name': 'Ethereum',
        'symbol': 'ETH',
        'decimal_places': 8,
        'network': 'Ethereum',
        'default_rate_usd': Decimal('2800.00'),
        'api_id': 'ethereum',
        'icon': 'ethereum',
        'popular': True
    },
    'LTC': {
        'name': 'Litecoin',
        'symbol': 'LTC',
        'decimal_places': 8,
        'network': 'Litecoin',
        'default_rate_usd': Decimal('95.00'),
        'api_id': 'litecoin',
        'icon': 'litecoin',
        'popular': True
    },
    
    # Stablecoins
    'USDT': {
        'name': 'Tether USD',
        'symbol': 'USDT',
        'decimal_places': 6,
        'network': 'Multiple',
        'default_rate_usd': Decimal('1.00'),
        'api_id': 'tether',
        'icon': 'tether',
        'popular': True
    },
    'USDC': {
        'name': 'USD Coin',
        'symbol': 'USDC',
        'decimal_places': 6,
        'network': 'Multiple',
        'default_rate_usd': Decimal('1.00'),
        'api_id': 'usd-coin',
        'icon': 'usd-coin',
        'popular': True
    },
    'BUSD': {
        'name': 'Binance USD',
        'symbol': 'BUSD',
        'decimal_places': 6,
        'network': 'BSC',
        'default_rate_usd': Decimal('1.00'),
        'api_id': 'binance-usd',
        'icon': 'binance-usd',
        'popular': False
    },
    
    # Major Altcoins
    'BNB': {
        'name': 'Binance Coin',
        'symbol': 'BNB',
        'decimal_places': 8,
        'network': 'BSC',
        'default_rate_usd': Decimal('320.00'),
        'api_id': 'binancecoin',
        'icon': 'binance-coin',
        'popular': True
    },
    'ADA': {
        'name': 'Cardano',
        'symbol': 'ADA',
        'decimal_places': 6,
        'network': 'Cardano',
        'default_rate_usd': Decimal('0.38'),
        'api_id': 'cardano',
        'icon': 'cardano',
        'popular': True
    },
    'XRP': {
        'name': 'Ripple',
        'symbol': 'XRP',
        'decimal_places': 6,
        'network': 'XRP Ledger',
        'default_rate_usd': Decimal('0.55'),
        'api_id': 'ripple',
        'icon': 'ripple',
        'popular': True
    },
    'SOL': {
        'name': 'Solana',
        'symbol': 'SOL',
        'decimal_places': 8,
        'network': 'Solana',
        'default_rate_usd': Decimal('22.50'),
        'api_id': 'solana',
        'icon': 'solana',
        'popular': True
    },
    'MATIC': {
        'name': 'Polygon',
        'symbol': 'MATIC',
        'decimal_places': 8,
        'network': 'Polygon',
        'default_rate_usd': Decimal('0.85'),
        'api_id': 'matic-network',
        'icon': 'polygon',
        'popular': True
    },
    'DOT': {
        'name': 'Polkadot',
        'symbol': 'DOT',
        'decimal_places': 8,
        'network': 'Polkadot',
        'default_rate_usd': Decimal('6.20'),
        'api_id': 'polkadot',
        'icon': 'polkadot',
        'popular': True
    },
    'AVAX': {
        'name': 'Avalanche',
        'symbol': 'AVAX',
        'decimal_places': 8,
        'network': 'Avalanche',
        'default_rate_usd': Decimal('35.50'),
        'api_id': 'avalanche-2',
        'icon': 'avalanche',
        'popular': True
    },
    'LINK': {
        'name': 'Chainlink',
        'symbol': 'LINK',
        'decimal_places': 8,
        'network': 'Ethereum',
        'default_rate_usd': Decimal('14.20'),
        'api_id': 'chainlink',
        'icon': 'chainlink',
        'popular': True
    },
    'UNI': {
        'name': 'Uniswap',
        'symbol': 'UNI',
        'decimal_places': 8,
        'network': 'Ethereum',
        'default_rate_usd': Decimal('6.80'),
        'api_id': 'uniswap',
        'icon': 'uniswap',
        'popular': False
    },
    'ATOM': {
        'name': 'Cosmos',
        'symbol': 'ATOM',
        'decimal_places': 6,
        'network': 'Cosmos',
        'default_rate_usd': Decimal('12.30'),
        'api_id': 'cosmos',
        'icon': 'cosmos',
        'popular': False
    },
    
    # Privacy Coins
    'XMR': {
        'name': 'Monero',
        'symbol': 'XMR',
        'decimal_places': 8,
        'network': 'Monero',
        'default_rate_usd': Decimal('145.00'),
        'api_id': 'monero',
        'icon': 'monero',
        'popular': False
    },
    'ZEC': {
        'name': 'Zcash',
        'symbol': 'ZEC',
        'decimal_places': 8,
        'network': 'Zcash',
        'default_rate_usd': Decimal('28.50'),
        'api_id': 'zcash',
        'icon': 'zcash',
        'popular': False
    },
    
    # DeFi Tokens
    'AAVE': {
        'name': 'Aave',
        'symbol': 'AAVE',
        'decimal_places': 8,
        'network': 'Ethereum',
        'default_rate_usd': Decimal('95.00'),
        'api_id': 'aave',
        'icon': 'aave',
        'popular': False
    },
    'COMP': {
        'name': 'Compound',
        'symbol': 'COMP',
        'decimal_places': 8,
        'network': 'Ethereum',
        'default_rate_usd': Decimal('48.00'),
        'api_id': 'compound-governance-token',
        'icon': 'compound',
        'popular': False
    },
    
    # Other Popular Coins
    'DOGE': {
        'name': 'Dogecoin',
        'symbol': 'DOGE',
        'decimal_places': 8,
        'network': 'Dogecoin',
        'default_rate_usd': Decimal('0.09'),
        'api_id': 'dogecoin',
        'icon': 'dogecoin',
        'popular': True
    },
    'SHIB': {
        'name': 'Shiba Inu',
        'symbol': 'SHIB',
        'decimal_places': 18,
        'network': 'Ethereum',
        'default_rate_usd': Decimal('0.000009'),
        'api_id': 'shiba-inu',
        'icon': 'shiba-inu',
        'popular': False
    },
    'TRX': {
        'name': 'TRON',
        'symbol': 'TRX',
        'decimal_places': 6,
        'network': 'TRON',
        'default_rate_usd': Decimal('0.068'),
        'api_id': 'tron',
        'icon': 'tron',
        'popular': False
    },
    'BCH': {
        'name': 'Bitcoin Cash',
        'symbol': 'BCH',
        'decimal_places': 8,
        'network': 'Bitcoin Cash',
        'default_rate_usd': Decimal('235.00'),
        'api_id': 'bitcoin-cash',
        'icon': 'bitcoin-cash',
        'popular': True
    },
    'ETC': {
        'name': 'Ethereum Classic',
        'symbol': 'ETC',
        'decimal_places': 8,
        'network': 'Ethereum Classic',
        'default_rate_usd': Decimal('20.50'),
        'api_id': 'ethereum-classic',
        'icon': 'ethereum-classic',
        'popular': False
    }
}

def get_popular_cryptocurrencies():
    """Get list of popular cryptocurrencies for main selection"""
    return {k: v for k, v in SUPPORTED_CRYPTOCURRENCIES.items() if v.get('popular', False)}

def get_all_cryptocurrencies():
    """Get all supported cryptocurrencies"""
    return SUPPORTED_CRYPTOCURRENCIES

def get_cryptocurrency_info(symbol):
    """Get detailed information about a specific cryptocurrency"""
    return SUPPORTED_CRYPTOCURRENCIES.get(symbol.upper())

def get_cryptocurrency_choices():
    """Get choices for form fields - popular currencies first"""
    popular = [(k, f"{v['name']} ({k})") for k, v in SUPPORTED_CRYPTOCURRENCIES.items() if v.get('popular', False)]
    others = [(k, f"{v['name']} ({k})") for k, v in SUPPORTED_CRYPTOCURRENCIES.items() if not v.get('popular', False)]
    
    # Add separator and combine
    choices = [('', '--- Popular Cryptocurrencies ---')] + popular + [('', '--- Other Cryptocurrencies ---')] + others
    return choices

def format_crypto_amount(amount, currency):
    """Format crypto amount with appropriate decimal places"""
    if not amount:
        return f"0 {currency}"
    
    crypto_info = get_cryptocurrency_info(currency)
    if crypto_info:
        decimal_places = crypto_info['decimal_places']
        return f"{amount:.{decimal_places}f} {currency}"
    
    # Default formatting
    return f"{amount:.8f} {currency}"

def get_minimum_payment_amount(currency):
    """Get minimum payment amount for a cryptocurrency"""
    crypto_info = get_cryptocurrency_info(currency)
    if not crypto_info:
        return Decimal('0.00000001')
    
    # Set reasonable minimums based on decimal places
    decimal_places = crypto_info['decimal_places']
    if decimal_places >= 8:
        return Decimal('0.00000001')
    elif decimal_places >= 6:
        return Decimal('0.000001')
    else:
        return Decimal('0.01')
