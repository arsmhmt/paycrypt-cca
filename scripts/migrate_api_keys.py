#!/usr/bin/env python3
"""
Database Migration Script: Add secret_key column to client_api_keys table
Run this to update existing API keys with secret keys
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.api_key import ClientApiKey
import secrets

def migrate_api_keys():
    """Add secret_key to existing API keys that don't have one"""
    app = create_app()
    
    with app.app_context():
        # Find API keys without secret_key
        api_keys_without_secret = ClientApiKey.query.filter(
            (ClientApiKey.secret_key == None) | (ClientApiKey.secret_key == '')
        ).all()
        
        print(f"Found {len(api_keys_without_secret)} API keys without secret keys")
        
        for api_key in api_keys_without_secret:
            # Generate new secret key
            api_key.secret_key = secrets.token_hex(32)
            
            # Generate webhook secret if missing
            if not api_key.webhook_secret:
                api_key.webhook_secret = secrets.token_hex(24)
                
            print(f"Updated API key '{api_key.name}' (ID: {api_key.id}) for client {api_key.client_id}")
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully updated {len(api_keys_without_secret)} API keys")

if __name__ == '__main__':
    migrate_api_keys()
