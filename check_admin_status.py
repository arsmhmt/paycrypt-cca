from app import create_app
from app.models import db, Client, User, Role

def check_admin_status(username):
    app = create_app()
    with app.app_context():
        # Check in User table first
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}")
            print(f"Email: {user.email}")
            if user.role:
                print(f"Role: {user.role.name}")
                print(f"Is admin: {'admin' in user.role.name.lower()}")
            else:
                print("No role assigned")
            return
        
        # Check in Client table if not found in User
        client = Client.query.filter_by(username=username).first()
        if client:
            print(f"Client found: {client.username}")
            print("Note: Client model doesn't have direct admin privileges in this system")
            return
            
        print(f"No user or client found with username: {username}")

if __name__ == "__main__":
    check_admin_status("paycrypt")
