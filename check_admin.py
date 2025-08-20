from app import create_app
from app.models import Client, User, db
import sys

def check_admin(username):
    app = create_app()
    with app.app_context():
        # Check in Client model
        client = Client.query.filter_by(username=username).first()
        if client:
            print(f"Found user '{username}' in Client table")
            print(f"Is admin: {client.is_admin if hasattr(client, 'is_admin') else 'is_admin attribute not found'}")
            return
        
        # Check in User model if exists
        if hasattr(sys.modules[__name__], 'User'):
            user = User.query.filter_by(username=username).first()
            if user:
                print(f"Found user '{username}' in User table")
                print(f"Is admin: {user.is_admin if hasattr(user, 'is_admin') else 'is_admin attribute not found'}")
                return
        
        print(f"User '{username}' not found in the database")

if __name__ == "__main__":
    check_admin("paycrypt")
