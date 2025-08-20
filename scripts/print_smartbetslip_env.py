#!/usr/bin/env python3
"""
Print SmartBetslip Integration Environment Variables
===================================================

This script prints the required environment variables for SmartBetslip integration.

Usage:
    python scripts/print_smartbetslip_env.py
"""

import sys
import os
import secrets

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Client
from app.models.api_key import ClientApiKey

def print_smartbetslip_env_vars():
    """Print SmartBetslip integration environment variables"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Find SmartBetslip client
            smartbetslip_client = Client.query.filter(
                Client.company_name.in_(['SBS', 'SmartBetslip'])
            ).first()
            
            if not smartbetslip_client:
                print("❌ SmartBetslip client not found!")
                return False
            
            # Get SmartBetslip API key
            api_key = ClientApiKey.query.filter_by(
                client_id=smartbetslip_client.id,
                is_active=True
            ).first()
            
            if not api_key:
                print("❌ SmartBetslip API key not found!")
                return False
            
            # Generate new secrets
            secret_key = secrets.token_hex(32)
            webhook_secret = secrets.token_hex(24)
            
            print("🔑 SmartBetslip Integration Environment Variables")
            print("=" * 60)
            print()
            print("# Add these to your .env file:")
            print()
            print(f"PAYCRYPT_API_KEY={api_key.key}")
            print(f"PAYCRYPT_SECRET_KEY={secret_key}")
            print(f"PAYCRYPT_WEBHOOK_SECRET={webhook_secret}")
            print(f"PAYCRYPT_BASE_URL=https://api.paycrypt.online/v1")
            print()
            print("# Additional configuration:")
            print(f"SMARTBETSLIP_CLIENT_ID={smartbetslip_client.id}")
            print(f"SMARTBETSLIP_COMPANY_NAME={smartbetslip_client.company_name}")
            print()
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    print_smartbetslip_env_vars()
