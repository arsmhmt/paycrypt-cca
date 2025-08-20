from flask import Blueprint, render_template, redirect, request, url_for, flash
auth_bp = Blueprint("auth", __name__)
from datetime import datetime
from flask_login import login_user, logout_user, current_user
from app.models import User, Client
from app.utils import check_password
from app import db
from app.forms import ClientLoginForm

auth_bp = Blueprint("auth", __name__)

# --- Client Login (Flask-Login expects endpoint 'auth.login') ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Route /login should show client login page only if not admin path
    # If user is authenticated and is admin, redirect to admin dashboard
    if current_user.is_authenticated:
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            return redirect(url_for("admin.admin_dashboard"))
        return redirect(url_for("client.client_dashboard"))
    return client_login()

# --- Register ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # TODO: Implement registration logic (form, validation, user creation, etc.)
    return render_template('auth/register.html', now=datetime.utcnow())

# --- Reset Password ---
@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    # TODO: Implement password reset logic (token validation, new password form, etc.)
    return render_template('auth/reset_password.html', now=datetime.utcnow())

# --- Forgot Password ---
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # TODO: Implement password reset logic (send email, etc.)
        from flask_babel import _
        flash(_('If your email exists in our system, you will receive a password reset link.'), 'info')
    return render_template('auth/forgot_password.html', now=datetime.utcnow())

# --- Client Login ---
@auth_bp.route("/client/login", methods=["GET", "POST"])
def client_login():
    form = ClientLoginForm()
    # Only redirect if the current user is a Client (prevents redirect loop for other user types)
    if current_user.is_authenticated and isinstance(current_user, Client):
        return redirect(url_for("client.client_dashboard"))

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # First try to find the User record (for admin-created clients)
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.client:
            # Check if the linked client is active
            client = user.client
            if client.is_active and not client.is_locked:
                login_user(user, remember=form.remember.data)
                return redirect(url_for("client.client_dashboard"))
        
        # Fallback: try direct Client authentication (for legacy clients)
        client = Client.query.filter_by(username=username).first()
        if client and client.check_password(password) and client.is_active and not client.is_locked:
            login_user(client, remember=form.remember.data)
            return redirect(url_for("client.client_dashboard"))
            
        from flask_babel import _
        flash(_("Invalid credentials"), "danger")

    return render_template("auth/client_login.html", form=form, now=datetime.utcnow())

# --- Admin Login ---
@auth_bp.route("/admin120724/login", methods=["GET", "POST"])
def admin_login():
    # Debug: Print session info
    print(f"[DEBUG] Admin login - Current user: {current_user}, is_authenticated: {current_user.is_authenticated}")
    
    if current_user.is_authenticated:
        # Debug: Print user attributes
        print(f"[DEBUG] User attributes: {dir(current_user)}")
        if hasattr(current_user, 'is_admin') and callable(current_user.is_admin):
            print(f"[DEBUG] is_admin() result: {current_user.is_admin()}")
        
        # Only redirect if user is actually an admin
        if hasattr(current_user, 'is_admin') and callable(current_user.is_admin) and current_user.is_admin():
            print("[DEBUG] User is admin, redirecting to admin dashboard")
            return redirect(url_for("admin.admin_dashboard"))
        # If not admin, log out and show login form
        print("[DEBUG] User is not an admin, logging out")
        logout_user()
        flash("You must be an admin to access this page.", "danger")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(f"[DEBUG] Login attempt - Username: {username}")

        from app.models import Role
        user = User.query.filter_by(username=username).filter(User.role.has(Role.name.in_(["superadmin", "admin"]))).first()
        print(f"[DEBUG] User found: {user}")
        
        if user and hasattr(user, 'check_password') and callable(user.check_password):
            print("[DEBUG] Checking password...")
            if user.check_password(password):
                print("[DEBUG] Password correct, logging in...")
                login_user(user)
                print(f"[DEBUG] Logged in as {user.username}, is_authenticated: {current_user.is_authenticated}")
                return redirect(url_for("admin.admin_dashboard"))
            else:
                print("[DEBUG] Invalid password")
        else:
            print("[DEBUG] User not found or invalid user type")
            
        flash("Invalid credentials", "danger")

    return render_template("auth/admin_login.html", now=datetime.utcnow())

# --- Logout for both ---
@auth_bp.route("/logout")
def logout():
    logout_user()
    # After logout, redirect to correct login page
    next_url = request.args.get('next')
    if next_url and next_url.startswith('/admin120724'):
        return redirect(url_for("auth.admin_login"))
    return redirect(url_for("auth.client_login"))
