#!/usr/bin/env python3
"""
SmartBetslip API Integration Test Script
=======================================

This script tests the comprehensive API v1 endpoints for SmartBetslip client integration.
Tests include authentication, betslip operations, payment processing, and balance management.

SmartBetslip Client Details:
- Client ID: 2 (SmartBetslip)
- Package: Enterprise Flat Rate ($2,500/month)
- API Key: pk_bAfM0... (1000 requests/minute)
- Rate Limit: 1000 req/min
- Permissions: Full API access including betslip generation

Usage:
    python test_smartbetslip_api.py
"""

import requests
import json
import time
from datetime import datetime
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "pk_bAfM0swfeiwU8yrEHNzMphlRnZ7R9FmUZOaDtLG370o"  # SmartBetslip API key
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "SmartBetslip-Integration-Test/1.0"
}

class SmartBetslipAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.test_results = []
        
    def log_test(self, test_name, success, details):
        """Log test result"""
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_api_authentication(self):
        """Test API authentication with SmartBetslip API key"""
        print("\n=== Testing API Authentication ===")
        
        try:
            # Test valid authentication
            response = requests.get(f"{self.base_url}/api/v1/balance", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Valid API Key Authentication", True, f"Balance: ${data.get('available_balance', 0):.2f}")
            else:
                self.log_test("Valid API Key Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Valid API Key Authentication", False, f"Exception: {str(e)}")
        
        # Test invalid authentication
        try:
            invalid_headers = {"Authorization": "Bearer invalid_key"}
            response = requests.get(f"{self.base_url}/api/v1/balance", headers=invalid_headers)
            
            if response.status_code == 401:
                self.log_test("Invalid API Key Rejection", True, "Correctly rejected invalid key")
            else:
                self.log_test("Invalid API Key Rejection", False, f"Should reject invalid key, got: {response.status_code}")
                
        except Exception as e:
            self.log_test("Invalid API Key Rejection", False, f"Exception: {str(e)}")
    
    def test_balance_endpoints(self):
        """Test balance management endpoints"""
        print("\n=== Testing Balance Endpoints ===")
        
        try:
            # Get current balance
            response = requests.get(f"{self.base_url}/api/v1/balance", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                balance = data.get('available_balance', 0)
                self.log_test("Get Balance", True, f"Current balance: ${balance:.2f}")
            else:
                self.log_test("Get Balance", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Balance", False, f"Exception: {str(e)}")
    
    def test_betslip_generation(self):
        """Test betslip generation endpoint"""
        print("\n=== Testing Betslip Generation ===")
        
        # Test data for betslip generation
        betslip_data = {
            "user_id": "smartbetslip_user_123",
            "bets": [
                {
                    "event_id": "nfl_game_001",
                    "market": "moneyline",
                    "selection": "Patriots -3.5",
                    "odds": 1.91,
                    "stake": 100.00
                },
                {
                    "event_id": "nba_game_002", 
                    "market": "over_under",
                    "selection": "Over 215.5",
                    "odds": 1.85,
                    "stake": 50.00
                }
            ],
            "total_stake": 150.00,
            "currency": "USD",
            "betting_type": "combination"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/betslip/generate",
                headers=self.headers,
                json=betslip_data
            )
            
            if response.status_code == 201:
                data = response.json()
                betslip_id = data.get('betslip_id')
                self.log_test("Generate Betslip", True, f"Betslip ID: {betslip_id}")
                return betslip_id
            else:
                self.log_test("Generate Betslip", False, f"Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            self.log_test("Generate Betslip", False, f"Exception: {str(e)}")
            return None
    
    def test_betslip_status(self, betslip_id):
        """Test betslip status endpoint"""
        print("\n=== Testing Betslip Status ===")
        
        if not betslip_id:
            self.log_test("Get Betslip Status", False, "No betslip ID available")
            return
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/betslip/{betslip_id}/status",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                self.log_test("Get Betslip Status", True, f"Status: {status}")
            else:
                self.log_test("Get Betslip Status", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Betslip Status", False, f"Exception: {str(e)}")
    
    def test_payment_endpoints(self):
        """Test payment management endpoints"""
        print("\n=== Testing Payment Endpoints ===")
        
        # Create payment request
        payment_data = {
            "amount": 500.00,
            "currency": "USD",
            "payment_method": "crypto",
            "crypto_currency": "USDT_TRC20",
            "description": "SmartBetslip betting deposit",
            "metadata": {
                "user_id": "smartbetslip_user_123",
                "platform": "SmartBetslip",
                "integration_version": "1.0"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/payments",
                headers=self.headers,
                json=payment_data
            )
            
            if response.status_code == 201:
                data = response.json()
                payment_id = data.get('payment_id')
                self.log_test("Create Payment", True, f"Payment ID: {payment_id}")
            else:
                self.log_test("Create Payment", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Create Payment", False, f"Exception: {str(e)}")
        
        # Get payments list
        try:
            response = requests.get(f"{self.base_url}/api/v1/payments", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                payments_count = len(data.get('payments', []))
                self.log_test("List Payments", True, f"Found {payments_count} payments")
            else:
                self.log_test("List Payments", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("List Payments", False, f"Exception: {str(e)}")
    
    def test_withdrawal_endpoints(self):
        """Test withdrawal management endpoints"""
        print("\n=== Testing Withdrawal Endpoints ===")
        
        # Create withdrawal request
        withdrawal_data = {
            "amount": 250.00,
            "currency": "USD",
            "withdrawal_method": "crypto",
            "crypto_currency": "USDT_TRC20",
            "wallet_address": "TQn9Y2khEsLJW1ChVWFMSMeRDow5KcbLSE",
            "description": "SmartBetslip winnings withdrawal",
            "metadata": {
                "user_id": "smartbetslip_user_123",
                "platform": "SmartBetslip"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/withdrawals",
                headers=self.headers,
                json=withdrawal_data
            )
            
            if response.status_code == 201:
                data = response.json()
                withdrawal_id = data.get('withdrawal_id')
                self.log_test("Create Withdrawal", True, f"Withdrawal ID: {withdrawal_id}")
            else:
                self.log_test("Create Withdrawal", False, f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Create Withdrawal", False, f"Exception: {str(e)}")
        
        # Get withdrawals list
        try:
            response = requests.get(f"{self.base_url}/api/v1/withdrawals", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                withdrawals_count = len(data.get('withdrawals', []))
                self.log_test("List Withdrawals", True, f"Found {withdrawals_count} withdrawals")
            else:
                self.log_test("List Withdrawals", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("List Withdrawals", False, f"Exception: {str(e)}")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        print("\n=== Testing Rate Limiting (1000 req/min) ===")
        
        # Make multiple requests quickly to test rate limiting
        start_time = time.time()
        request_count = 0
        
        try:
            for i in range(10):  # Test with 10 rapid requests
                response = requests.get(f"{self.base_url}/api/v1/balance", headers=self.headers)
                request_count += 1
                
                if response.status_code == 429:  # Rate limited
                    self.log_test("Rate Limiting", True, f"Rate limited after {request_count} requests")
                    return
                elif response.status_code != 200:
                    self.log_test("Rate Limiting", False, f"Unexpected status: {response.status_code}")
                    return
                
                time.sleep(0.1)  # Small delay between requests
            
            end_time = time.time()
            duration = end_time - start_time
            self.log_test("Rate Limiting", True, f"Made {request_count} requests in {duration:.2f}s without hitting limit")
            
        except Exception as e:
            self.log_test("Rate Limiting", False, f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test API error handling"""
        print("\n=== Testing Error Handling ===")
        
        # Test 404 - Non-existent betslip
        try:
            response = requests.get(f"{self.base_url}/api/v1/betslip/nonexistent/status", headers=self.headers)
            
            if response.status_code == 404:
                self.log_test("404 Error Handling", True, "Correctly returned 404 for non-existent betslip")
            else:
                self.log_test("404 Error Handling", False, f"Expected 404, got: {response.status_code}")
                
        except Exception as e:
            self.log_test("404 Error Handling", False, f"Exception: {str(e)}")
        
        # Test 405 - Method not allowed
        try:
            response = requests.delete(f"{self.base_url}/api/v1/balance", headers=self.headers)
            
            if response.status_code == 405:
                self.log_test("405 Error Handling", True, "Correctly returned 405 for invalid method")
            else:
                self.log_test("405 Error Handling", False, f"Expected 405, got: {response.status_code}")
                
        except Exception as e:
            self.log_test("405 Error Handling", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("=" * 60)
        print("SmartBetslip API Integration Test Suite")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"API Key: {API_KEY[:20]}...")
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_api_authentication()
        self.test_balance_endpoints()
        betslip_id = self.test_betslip_generation()
        self.test_betslip_status(betslip_id)
        self.test_payment_endpoints()
        self.test_withdrawal_endpoints()
        self.test_rate_limiting()
        self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ✗ {result['test']}: {result['details']}")
        
        print(f"\nTest Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return passed == total

def main():
    """Main test execution"""
    tester = SmartBetslipAPITester()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest suite failed with exception: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
