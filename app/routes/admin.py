from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Client
from app.forms import ClientForm
from app import db
from app.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin120724")

from flask_babel import _

# --- Admin Dashboard ---
@admin_bp.route("/dashboard")
@login_required
@admin_required
def admin_dashboard():
    # Debug logging
    print(f"[DEBUG] Admin dashboard - Current user: {current_user}, is_authenticated: {current_user.is_authenticated}")
    print(f"[DEBUG] User attributes: {dir(current_user)}")
    if hasattr(current_user, 'role'):
        print(f"[DEBUG] User role: {getattr(current_user.role, 'name', 'No role')}")
    
    try:
        clients = Client.query.all()
        stats = {
            'pending_withdrawals': 0,
            'total_clients': len(clients),
            'active_clients_change': 0,
            'success_rate': 0,
            'success_rate_change': 0,
            'total_commission': 0,
            'commission_change': 0,
            'volume_24h': 0,
        }
        import datetime
        current_time = datetime.datetime.now()
        
        print(f"[DEBUG] Admin dashboard rendered successfully")
    except Exception as e:
        print(f"[ERROR] Error in admin dashboard: {str(e)}")
        raise
    return render_template("admin/dashboard.html", clients=clients, stats=stats, current_time=current_time)

    # --- Add Client ---
@admin_bp.route("/clients/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_client():
    from app.models import ClientPackage, ClientType, User, Role
    packages = ClientPackage.query.filter_by(status='ACTIVE').order_by(ClientPackage.id).all()
    form = ClientForm()
    # Set choices for package_id dropdown
    form.package_id.choices = [(p.id, p.name) for p in packages]
    # Set default to Enterprise Flat Rate if available
    for p in packages:
        if 'enterprise' in p.name.lower():
            form.package_id.default = p.id
            break
    form.process(request.form)
    if form.validate_on_submit():
        try:
            # Ensure client role exists
            client_role = Role.query.filter_by(name='client').first()
            if not client_role:
                # Create client role if it doesn't exist
                client_role = Role(name='client', description='Client user role')
                db.session.add(client_role)
                db.session.flush()  # Ensure role is created before using it
            
            # First create the User record for authentication
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=client_role  # Assign client role directly
            )
            if form.password.data:
                user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.flush()  # Flush to get the user.id
            
            # Then create the Client record linked to the User
            client = Client(
                user_id=user.id,  # Link to the User record
                username=form.username.data,
                email=form.email.data,
                company_name=form.company_name.data,
                name=form.name.data,
                phone=form.phone.data,
                website=form.website.data,
                address=form.address.data,
                city=form.city.data,
                country=form.country.data,
                postal_code=form.postal_code.data,
                tax_id=form.tax_id.data,
                vat_number=form.vat_number.data,
                registration_number=form.registration_number.data,
                contact_person=form.contact_person.data,
                contact_email=form.contact_email.data,
                contact_phone=form.contact_phone.data,
                notes=form.notes.data,
                rate_limit=form.rate_limit.data,
                theme_color=form.theme_color.data,
                deposit_commission_rate=form.deposit_commission_rate.data,
                withdrawal_commission_rate=form.withdrawal_commission_rate.data,
                balance=form.balance.data,
                is_active=form.is_active.data,
                is_verified=form.is_verified.data,
                package_id=form.package_id.data
            )
            if form.password.data:
                client.set_password(form.password.data)  # Also set on client for backup
            
            db.session.add(client)
            db.session.commit()
            flash(_("Client and user account created successfully"), "success")
            return redirect(url_for("admin.list_clients"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating client: {str(e)}", "error")
            return render_template("admin/client_form.html", form=form, client=None, title="Add Client")
    return render_template("admin/client_form.html", form=form, client=None, title="Add Client")
# --- View All Clients ---
@admin_bp.route("/clients")
@login_required
@admin_required
def list_clients():
    from flask import request
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    status = request.args.get('status', '', type=str)
    
    # Build query
    query = Client.query
    
    # Apply search filter
    if search:
        query = query.filter(Client.company_name.contains(search) | 
                           Client.email.contains(search))
    
    # Apply status filter
    if status:
        query = query.filter(Client.status == status)
    
    # Get paginated results
    clients = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template("admin/clients/list.html", 
                         clients=clients, 
                         search=search, 
                         status=status, 
                         per_page=per_page)




# --- Edit Client ---
@admin_bp.route("/clients/<int:client_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)

    if request.method == "POST":
        client.email = request.form["email"]
        client.plan_type = request.form["plan_type"]
        if client.plan_type == "commission":
            client.commission_rate = float(request.form["commission_rate"])
        db.session.commit()
        flash("Client updated", "success")
        return redirect(url_for("admin.list_clients"))

    return render_template("admin/clients/view_simple.html", client=client)


# --- Delete Client ---
@admin_bp.route("/clients/<int:client_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash("Client deleted", "info")
    return redirect(url_for("admin.list_clients"))
    
# Payments list route
@admin_bp.route('/payments')
@login_required
@admin_required
def payments_list():
    # Add logic to fetch and display payments
    return render_template('admin/payments.html')

# Wallet Providers route
@admin_bp.route('/wallet-providers')
@login_required
@admin_required
def wallet_providers():
    # Add logic to fetch and display wallet providers
    return render_template('admin/wallet_providers.html')

# Wallet History route
@admin_bp.route('/wallet-history')
@login_required
@admin_required
def wallet_history():
    # Add logic to fetch and display wallet history
    return render_template('admin/wallet_history.html')

# Wallet Balances route
@admin_bp.route('/wallet-balances')
@login_required
@admin_required
def wallet_balances():
    # Add logic to fetch and display wallet balances
    return render_template('admin/wallet_balances.html')

# Audit Trail route
@admin_bp.route('/audit-trail')
@login_required
@admin_required
def audit_trail():
    # Add logic to fetch and display audit trail
    return render_template('admin/audit_trail.html')

# Access Control route
@admin_bp.route('/access-control')
@login_required
@admin_required
def access_control():
    # Add logic to fetch and display access control
    return render_template('admin/access_control.html')

# Settings route
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    # Add logic to fetch and update settings
    return render_template('admin/settings.html')

# Support Tickets route
@admin_bp.route('/support-tickets')
@login_required
@admin_required
def support_tickets():
    # Add logic to fetch and display support tickets
    return render_template('admin/support_tickets.html')

# API Docs route
@admin_bp.route('/api-docs')
@login_required
@admin_required
def api_docs():
    # Add logic to fetch and display API documentation
    return render_template('admin/api_docs.html')
