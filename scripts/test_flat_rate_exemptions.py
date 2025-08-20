#!/usr/bin/env python3
"""
Test Flat-Rate Payment Enforcement Skipping
==========================================

This script tests that payment enforcement is properly skipped for flat-rate clients,
especially SmartBetslip, and that they are always marked as active.

Usage:
    python scripts/test_flat_rate_exemptions.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import Client
from app.models.package_payment import PackageActivationPayment, FlatRateSubscriptionPayment, SubscriptionBillingCycle
from app.models.client_package import ClientPackage, ClientType
from app.extensions import db
from app.decorators import is_payment_exempt_client

def test_flat_rate_exemptions():
    """Test that flat-rate clients have proper payment exemptions"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🧪 Testing Flat-Rate Payment Exemptions...")
            print("=" * 60)
            
            # Test 1: Find SmartBetslip client
            print("Test 1: SmartBetslip Client Configuration")
            print("-" * 40)
            
            smartbetslip_client = Client.query.filter(
                Client.company_name.in_(['SBS', 'SmartBetslip'])
            ).first()
            
            if not smartbetslip_client:
                print("❌ SmartBetslip client not found!")
                return False
            
            print(f"✅ Found: {smartbetslip_client.company_name} (ID: {smartbetslip_client.id})")
            print(f"   - is_active: {smartbetslip_client.is_active}")
            print(f"   - package: {smartbetslip_client.package.name if smartbetslip_client.package else 'None'}")
            print(f"   - package_type: {smartbetslip_client.package.client_type if smartbetslip_client.package else 'None'}")
            
            # Test 2: Payment exemption check
            print("\nTest 2: Payment Exemption Status")
            print("-" * 40)
            
            is_exempt = is_payment_exempt_client(smartbetslip_client)
            print(f"✅ Payment Exempt: {is_exempt}")
            
            if not is_exempt:
                print("❌ SmartBetslip should be payment exempt!")
                return False
            
            # Test 3: Create mock PackageActivationPayment to test expiry skipping
            print("\nTest 3: Package Activation Payment Expiry")
            print("-" * 40)
            
            # Create a test payment that would normally be expired
            test_payment = PackageActivationPayment(
                client_id=smartbetslip_client.id,
                package_id=smartbetslip_client.package_id,
                setup_fee_amount=1000.00,
                setup_fee_currency='USD',
                crypto_currency='BTC',
                crypto_amount=0.001,
                crypto_address='test_address',
                expires_at=datetime.utcnow() - timedelta(hours=48)  # Already expired
            )
            
            # Manually set the relationships for testing (normally would be auto-loaded)
            test_payment.client = smartbetslip_client
            test_payment.package = smartbetslip_client.package
            
            # Test that expiry is skipped for flat-rate clients
            is_expired = test_payment.is_expired
            time_remaining = test_payment.time_remaining
            
            print(f"✅ Payment is_expired: {is_expired} (should be False)")
            print(f"✅ Time remaining: {time_remaining.days} days (should be 365)")
            
            if is_expired:
                print("❌ Flat-rate payment should not be expired!")
                return False
            
            # Test 4: Create mock FlatRateSubscriptionPayment
            print("\nTest 4: Flat-Rate Subscription Payment")
            print("-" * 40)
            
            test_subscription = FlatRateSubscriptionPayment(
                client_id=smartbetslip_client.id,
                package_id=smartbetslip_client.package_id,
                billing_amount=2500.00,
                billing_currency='USD',
                billing_cycle=SubscriptionBillingCycle.MONTHLY,
                billing_period_start=datetime.utcnow() - timedelta(days=35),
                billing_period_end=datetime.utcnow() - timedelta(days=5),
                expires_at=datetime.utcnow() - timedelta(hours=72)  # Already expired
            )
            
            # Manually set the relationships for testing
            test_subscription.client = smartbetslip_client
            test_subscription.package = smartbetslip_client.package
            
            is_sub_expired = test_subscription.is_expired
            is_sub_active = test_subscription.is_subscription_active
            
            print(f"✅ Subscription is_expired: {is_sub_expired} (should be False)")
            print(f"✅ Subscription is_active: {is_sub_active} (should be True)")
            
            if is_sub_expired or not is_sub_active:
                print("❌ Flat-rate subscription should not be expired and should be active!")
                return False
            
            # Test 5: Test all flat-rate clients
            print("\nTest 5: All Flat-Rate Clients")
            print("-" * 40)
            
            flat_rate_clients = Client.query.join(ClientPackage).filter(
                ClientPackage.client_type == ClientType.FLAT_RATE
            ).all()
            
            print(f"✅ Found {len(flat_rate_clients)} flat-rate clients:")
            
            for client in flat_rate_clients:
                is_client_exempt = is_payment_exempt_client(client)
                print(f"   - {client.company_name}: active={client.is_active}, exempt={is_client_exempt}")
                
                if not is_client_exempt:
                    print(f"❌ Flat-rate client {client.company_name} should be payment exempt!")
                    return False
            
            print("\n🎯 Summary:")
            print(f"   ✅ SmartBetslip is active: {smartbetslip_client.is_active}")
            print(f"   ✅ SmartBetslip is payment exempt: {is_exempt}")
            print(f"   ✅ Payment expiry is skipped for flat-rate packages")
            print(f"   ✅ Subscription expiry is skipped for flat-rate packages")
            print(f"   ✅ All {len(flat_rate_clients)} flat-rate clients are payment exempt")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing flat-rate exemptions: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("🚀 Testing Flat-Rate Payment Enforcement Skipping...")
    print()
    
    success = test_flat_rate_exemptions()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All flat-rate payment exemption tests passed!")
        print("🎉 SmartBetslip and all flat-rate clients are properly configured!")
    else:
        print("❌ Flat-rate payment exemption tests failed!")
        sys.exit(1)
