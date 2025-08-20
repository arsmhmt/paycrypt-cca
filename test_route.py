#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_rugchecker_route():
    app = create_app()
    
    with app.test_client() as client:
        print("Testing rugchecker routes...")
        
        # Test /tools/rugchecker route
        response = client.get('/tools/rugchecker')
        print(f"GET /tools/rugchecker - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.data.decode()}")
        
        # Test /tools/rugcheck route
        response = client.get('/tools/rugcheck')
        print(f"GET /tools/rugcheck - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.data.decode()}")
            
        # List all registered routes
        print("\nAll registered routes:")
        for rule in app.url_map.iter_rules():
            if 'tools' in rule.rule or 'rug' in rule.rule:
                print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods)}]")

if __name__ == '__main__':
    test_rugchecker_route()
