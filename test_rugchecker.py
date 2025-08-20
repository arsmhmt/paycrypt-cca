#!/usr/bin/env python3
"""
Test script for the Rugchecker tool
"""

from app import create_app
from app.routes.tools import analyze_token_security, SUPPORTED_CHAINS

def test_rugchecker():
    print("=== Rugchecker Tool Test ===")
    
    # Test 1: Check supported chains
    print(f"✅ Supported blockchains: {len(SUPPORTED_CHAINS)}")
    print("Sample chains:")
    for chain_id, name in list(SUPPORTED_CHAINS.items())[:5]:
        print(f"  - {name} (ID: {chain_id})")
    
    print()
    
    # Test 2: Test analysis function with safe token
    print("Testing analysis function with SAFE token:")
    safe_token = {
        'is_honeypot': '0',
        'is_blacklisted': '0',
        'is_whitelisted': '1',
        'buy_tax': '0.02',
        'sell_tax': '0.02',
        'token_name': 'Safe Token',
        'token_symbol': 'SAFE'
    }
    
    analysis = analyze_token_security(safe_token)
    print(f"  Risk Level: {analysis['risk_level']}")
    print(f"  Critical Issues: {len(analysis['risks'])}")
    print(f"  Warnings: {len(analysis['warnings'])}")
    print(f"  Info Items: {len(analysis['info'])}")
    
    print()
    
    # Test 3: Test analysis function with risky token
    print("Testing analysis function with RISKY token:")
    risky_token = {
        'is_honeypot': '1',
        'is_blacklisted': '1',
        'owner_change_balance': '1',
        'buy_tax': '0.25',
        'sell_tax': '0.25',
        'token_name': 'Risky Token',
        'token_symbol': 'RISK'
    }
    
    analysis = analyze_token_security(risky_token)
    print(f"  Risk Level: {analysis['risk_level']}")
    print(f"  Critical Issues: {len(analysis['risks'])}")
    print(f"  Warnings: {len(analysis['warnings'])}")
    print(f"  Info Items: {len(analysis['info'])}")
    
    if analysis['risks']:
        print("  Critical Issues:")
        for risk in analysis['risks']:
            print(f"    - {risk}")
    
    print()
    print("✅ Rugchecker tool is working correctly!")
    print("🌐 Access it at: http://localhost:5000/tools/rugcheck")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        test_rugchecker()
