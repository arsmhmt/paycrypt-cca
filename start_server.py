#!/usr/bin/env python3
"""
Start the Flask development server for testing rugchecker
"""

from app import create_app

if __name__ == "__main__":
    app = create_app()
    print("🚀 Starting Paycrypt CCA with Rugchecker Tool...")
    print("📍 Rugchecker available at: http://localhost:5000/tools/rugcheck")
    print("🔧 Admin panel at: http://localhost:5000/admin120724")
    print("👤 Client panel at: http://localhost:5000/client")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
