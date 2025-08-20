#!/usr/bin/env python3
"""
Generate SmartBetslip Integration Environment Variables
======================================================

This script generates the required environment variables for SmartBetslip
integration, including API keys, secrets, and webhook configuration.

Usage:
    python scripts/generate_smartbetslip_env.py
"""

import sys
import os
import secrets
import string

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Client
from app.models.api_key import ClientApiKey

def generate_secret_key(length=64):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + "_-"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_webhook_secret(length=32):
    """Generate a webhook secret for HMAC verification"""
    return secrets.token_urlsafe(length)

def get_smartbetslip_keys():
    """Get SmartBetslip API keys and generate integration environment variables"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Find SmartBetslip client
            smartbetslip = Client.query.filter(
                Client.company_name.in_(['SBS', 'SmartBetslip'])
            ).first()
            
            if not smartbetslip:
                print("❌ SmartBetslip client not found!")
                return False
            
            print(f"✅ Found SmartBetslip client: {smartbetslip.company_name} (ID: {smartbetslip.id})")
            
            # Get active API key
            api_key = ClientApiKey.query.filter_by(
                client_id=smartbetslip.id,
                is_active=True
            ).first()
            
            if not api_key:
                print("❌ No active API key found for SmartBetslip!")
                return False
            
            print(f"✅ Found active API key: {api_key.name}")
            
            # Generate environment variables
            print("\n" + "=" * 60)
            print("SMARTBETSLIP INTEGRATION ENVIRONMENT VARIABLES")
            print("=" * 60)
            
            print("# SmartBetslip Integration Configuration")
            print("# Add these to your .env file or environment variables")
            print()
            
            # PAYCRYPT_API_KEY - The public API key for SmartBetslip
            print(f"PAYCRYPT_API_KEY={api_key.key}")
            
            # PAYCRYPT_SECRET_KEY - Generate a new secret key for encryption/signing
            secret_key = generate_secret_key()
            print(f"PAYCRYPT_SECRET_KEY={secret_key}")
            
            # PAYCRYPT_WEBHOOK_SECRET - Generate webhook secret for HMAC verification
            webhook_secret = api_key.webhook_secret if hasattr(api_key, 'webhook_secret') and api_key.webhook_secret else generate_webhook_secret()
            print(f"PAYCRYPT_WEBHOOK_SECRET={webhook_secret}")
            
            # PAYCRYPT_BASE_URL - The base URL for API calls
            print(f"PAYCRYPT_BASE_URL=https://api.paycrypt.online/v1")
            
            print()
            print("# Additional Configuration (Optional)")
            print(f"PAYCRYPT_CLIENT_ID={smartbetslip.id}")
            print(f"PAYCRYPT_CLIENT_NAME={smartbetslip.company_name}")
            print(f"PAYCRYPT_RATE_LIMIT={api_key.rate_limit if hasattr(api_key, 'rate_limit') else 1000}")
            
            # Show key details
            print()
            print("=" * 60)
            print("KEY DETAILS")
            print("=" * 60)
            print(f"Client: {smartbetslip.company_name}")
            print(f"Package: {smartbetslip.package.name if smartbetslip.package else 'None'}")
            print(f"API Key Name: {api_key.name}")
            print(f"API Key: {api_key.key}")
            print(f"Active: {api_key.is_active}")
            print(f"Created: {api_key.created_at}")
            print(f"Permissions: {api_key.permissions if hasattr(api_key, 'permissions') else 'Full Access'}")
            
            if hasattr(api_key, 'webhook_secret') and api_key.webhook_secret:
                print(f"Existing Webhook Secret: {api_key.webhook_secret}")
            else:
                print(f"Generated Webhook Secret: {webhook_secret}")
            
            print()
            print("🔐 SECURITY NOTES:")
            print("- Keep these keys secure and never commit them to version control")
            print("- Use environment variables in production")
            print("- Rotate keys regularly for security")
            print("- Webhook secret is used for HMAC-SHA256 signature verification")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating SmartBetslip environment variables: {e}")
            import traceback
            traceback.print_exc()
            return False

def update_env_file():
    """Update the .env file with SmartBetslip variables"""
    env_file_path = ".env"
    
    if not os.path.exists(env_file_path):
        print(f"❌ .env file not found at {env_file_path}")
        return False
    
    # Read existing .env content
    with open(env_file_path, 'r') as f:
        lines = f.readlines()
    
    # Generate the variables
    app = create_app()
    with app.app_context():
        smartbetslip = Client.query.filter(Client.company_name.in_(['SBS', 'SmartBetslip'])).first()
        if not smartbetslip:
            return False
            
        api_key = ClientApiKey.query.filter_by(client_id=smartbetslip.id, is_active=True).first()
        if not api_key:
            return False
        
        # Prepare new variables
        new_vars = {
            'PAYCRYPT_API_KEY': api_key.key,
            'PAYCRYPT_SECRET_KEY': generate_secret_key(),
            'PAYCRYPT_WEBHOOK_SECRET': api_key.webhook_secret if hasattr(api_key, 'webhook_secret') and api_key.webhook_secret else generate_webhook_secret(),
            'PAYCRYPT_BASE_URL': 'https://api.paycrypt.online/v1',
            'PAYCRYPT_CLIENT_ID': str(smartbetslip.id),
            'PAYCRYPT_CLIENT_NAME': smartbetslip.company_name,
        }
        
        # Check if variables already exist and update them
        updated_lines = []
        added_vars = set()
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                key = line.split('=')[0].strip()
                if key in new_vars:
                    updated_lines.append(f"{key}={new_vars[key]}\n")
                    added_vars.add(key)
                else:
                    updated_lines.append(line + '\n')
            else:
                updated_lines.append(line + '\n')
        
        # Add new variables that weren't in the file
        if added_vars != set(new_vars.keys()):
            updated_lines.append('\n# SmartBetslip Integration Configuration\n')
            for key, value in new_vars.items():
                if key not in added_vars:
                    updated_lines.append(f"{key}={value}\n")
        
        # Write back to .env file
        with open(env_file_path, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"✅ Updated {env_file_path} with SmartBetslip configuration")
        return True

if __name__ == "__main__":
    print("🚀 Generating SmartBetslip Integration Environment Variables...")
    print()
    
    success = get_smartbetslip_keys()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SmartBetslip environment variables generated successfully!")
        
        response = input("\n📝 Would you like to update the .env file automatically? (y/n): ")
        if response.lower() in ['y', 'yes']:
            if update_env_file():
                print("✅ .env file updated successfully!")
            else:
                print("❌ Failed to update .env file")
        else:
            print("📋 Please copy the variables above and add them to your .env file manually.")
    else:
        print("❌ Failed to generate SmartBetslip environment variables!")
        sys.exit(1)
