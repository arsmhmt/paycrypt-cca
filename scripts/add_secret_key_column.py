#!/usr/bin/env python3
"""
Database Migration Script: Add secret_key column to client_api_keys table
This script will first add the column, then populate it with values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.api_key import ClientApiKey
import secrets

def migrate_database():
    """Add secret_key column and populate existing API keys"""
    app = create_app()
    
    with app.app_context():
        # Check if column already exists by trying to query it
        try:
            # Try to access the secret_key column
            test_query = db.session.execute(
                db.text("SELECT secret_key FROM client_api_keys LIMIT 1")
            ).fetchone()
            print("secret_key column already exists")
        except Exception as e:
            if "no such column" in str(e):
                print("Adding secret_key column to client_api_keys table...")
                
                # Add the secret_key column
                db.session.execute(
                    db.text("ALTER TABLE client_api_keys ADD COLUMN secret_key VARCHAR(64)")
                )
                db.session.commit()
                print("Successfully added secret_key column")
            else:
                print(f"Unexpected error: {e}")
                return
        
        # Now populate API keys without secret keys
        try:
            # Use raw SQL to find records with NULL secret_key 
            result = db.session.execute(
                db.text("SELECT id, name, client_id FROM client_api_keys WHERE secret_key IS NULL OR secret_key = ''")
            ).fetchall()
            
            print(f"Found {len(result)} API keys without secret keys")
            
            for row in result:
                api_key_id, name, client_id = row
                secret_key = secrets.token_hex(32)
                
                # Update using raw SQL
                db.session.execute(
                    db.text("UPDATE client_api_keys SET secret_key = :secret_key WHERE id = :id"),
                    {"secret_key": secret_key, "id": api_key_id}
                )
                
                print(f"Updated API key '{name}' (ID: {api_key_id}) for client {client_id}")
            
            # Commit all changes
            db.session.commit()
            print(f"Successfully updated {len(result)} API keys with secret keys")
            
        except Exception as e:
            print(f"Error updating API keys: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_database()
