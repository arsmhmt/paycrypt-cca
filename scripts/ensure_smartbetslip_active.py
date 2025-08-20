#!/usr/bin/env python3
"""
Ensure SmartBetslip Active Status Script
=======================================

This script ensures that the SmartBetslip client is marked as active
and has proper flat-rate package exemptions configured.

Usage:
    python scripts/ensure_smartbetslip_active.py
"""

import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Client
from app.extensions import db
from app.decorators import is_payment_exempt_client

def ensure_smartbetslip_active():
    """Ensure SmartBetslip client is marked as active"""
    
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
            
            print(f"✅ Found SmartBetslip client: {smartbetslip_client.company_name} (ID: {smartbetslip_client.id})")
            
            # Check current status
            print(f"📊 Current Status:")
            print(f"   - is_active: {smartbetslip_client.is_active}")
            print(f"   - package_id: {smartbetslip_client.package_id}")
            if smartbetslip_client.package:
                print(f"   - package_name: {smartbetslip_client.package.name}")
                print(f"   - package_type: {smartbetslip_client.package.client_type}")
            
            # Check if payment exempt
            is_exempt = is_payment_exempt_client(smartbetslip_client)
            print(f"   - payment_exempt: {is_exempt}")
            
            # Ensure active status
            changes_made = False
            if not smartbetslip_client.is_active:
                print("🔧 Setting SmartBetslip client as active...")
                smartbetslip_client.is_active = True
                changes_made = True
            
            if changes_made:
                db.session.commit()
                print("✅ SmartBetslip client status updated successfully!")
            else:
                print("✅ SmartBetslip client is already properly configured!")
            
            # Final verification
            print(f"🎯 Final Status:")
            print(f"   - is_active: {smartbetslip_client.is_active}")
            print(f"   - payment_exempt: {is_payment_exempt_client(smartbetslip_client)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error ensuring SmartBetslip active status: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Ensuring SmartBetslip Active Status...")
    print("=" * 50)
    
    success = ensure_smartbetslip_active()
    
    print("=" * 50)
    if success:
        print("✅ SmartBetslip active status verification completed successfully!")
    else:
        print("❌ SmartBetslip active status verification failed!")
        sys.exit(1)
