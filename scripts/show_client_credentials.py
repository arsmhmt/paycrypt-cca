#!/usr/bin/env python3
"""
Demo Script: Show API Key Credentials for Each Client
This script demonstrates how clients can access their API integration credentials
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.api_key import ClientApiKey
from app.models.client import Client

def show_client_credentials():
    """Display API credentials for all clients"""
    app = create_app()
    
    with app.app_context():
        # Get all clients with API keys
        clients = Client.query.all()
        base_url = app.config.get('PAYCRYPT_BASE_URL', 'https://api.paycrypt.online/v1')
        
        print("=" * 80)
        print("PAYCRYPT API INTEGRATION CREDENTIALS")
        print("=" * 80)
        print()
        
        for client in clients:
            api_keys = ClientApiKey.query.filter_by(client_id=client.id).all()
            
            if api_keys:
                print(f"CLIENT: {client.company_name or client.name or client.email}")
                print(f"CLIENT ID: {client.id}")
                print(f"CLIENT TYPE: {'Enterprise Flat Rate' if client.package and 'flat' in client.package.name.lower() else 'Commission Based'}")
                print("-" * 60)
                
                for i, api_key in enumerate(api_keys, 1):
                    print(f"\nAPI KEY #{i}: {api_key.name}")
                    print(f"Status: {'Active' if api_key.is_active else 'Revoked'}")
                    print()
                    print("INTEGRATION CREDENTIALS:")
                    print(f"PAYCRYPT_API_KEY={api_key.key}")
                    print(f"PAYCRYPT_SECRET_KEY={api_key.secret_key}")
                    print(f"PAYCRYPT_WEBHOOK_SECRET={api_key.webhook_secret}")
                    print(f"PAYCRYPT_BASE_URL={base_url}")
                    print()
                    print("USAGE INFORMATION:")
                    print(f"• Rate Limit: {api_key.rate_limit} requests/minute")
                    print(f"• Created: {api_key.created_at.strftime('%Y-%m-%d %H:%M')}")
                    print(f"• Usage Count: {api_key.usage_count or 0}")
                    print()
                    print("EXAMPLE API REQUEST (curl):")
                    print(f'curl -X POST "{base_url}/payments" \\')
                    print(f'  -H "Authorization: Bearer {api_key.key}" \\')
                    print(f'  -H "X-Secret-Key: {api_key.secret_key}" \\')
                    print(f'  -H "Content-Type: application/json" \\')
                    print(f'  -d \'{{"amount": 100.00, "currency": "USDT"}}\'')
                    
                print("\n" + "=" * 80)
                print()
        
        print("\nACCESS CREDENTIALS VIA WEB INTERFACE:")
        print(f"• Client Login: http://127.0.0.1:8000/client/login")
        print(f"• API Keys Management: http://127.0.0.1:8000/client/api-keys")
        print(f"• API Documentation: http://127.0.0.1:8000/client/api-docs")
        print()

if __name__ == '__main__':
    show_client_credentials()
