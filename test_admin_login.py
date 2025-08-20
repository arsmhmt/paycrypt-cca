from app import create_app
from app.models import db, User, Role, Client

def test_admin_login():
    app = create_app()
    with app.app_context():
        # Find the user
        user = User.query.filter_by(username='paycrypt').first()
        if not user:
            print("User 'paycrypt' not found in User table")
            return
            
        print(f"User found: {user.username}")
        print(f"Email: {user.email}")
        
        # Check role
        if user.role:
            print(f"Role: {user.role.name}")
            print(f"Is admin: {user.is_admin()}")
        else:
            print("No role assigned to user")
        
        # Verify password - you'll need to enter the actual password here
        password = "Aylin*2024+"  # From your .env file
        password_correct = user.check_password(password)
        print(f"Password check: {'Correct' if password_correct else 'Incorrect'}")
        
        # Check if user is authenticated as admin
        from flask_login import login_user, current_user
        from flask import g
        with app.test_request_context():
            login_user(user)
            print(f"Logged in as: {current_user.username}")
            print(f"Is authenticated: {current_user.is_authenticated}")
            print(f"Is admin: {hasattr(current_user, 'is_admin') and current_user.is_admin()}")
            print(f"Current user type: {type(current_user).__name__}")

if __name__ == "__main__":
    test_admin_login()
