import secrets
import string

def generate_api_key(length=32):
    """
    Generate a secure random API key.
    
    Args:
        length (int): Length of the API key to generate. Default is 32.
        
    Returns:
        str: A secure random string suitable for use as an API key.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secure_token(length=64):
    """
    Generate a secure random token for various authentication purposes.
    
    Args:
        length (int): Length of the token to generate. Default is 64.
        
    Returns:
        str: A secure random string.
    """
    return secrets.token_urlsafe(length)

def is_valid_api_key(api_key, min_length=16):
    """
    Validate that an API key meets security requirements.
    
    Args:
        api_key (str): The API key to validate.
        min_length (int): Minimum required length for the API key. Default is 16.
        
    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    if not api_key or len(api_key) < min_length:
        return False
    # Check if the API key contains only alphanumeric characters
    return all(c.isalnum() for c in api_key)
