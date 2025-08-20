from flask import Blueprint, render_template

withdrawal_admin = Blueprint('withdrawal_admin', __name__, url_prefix='/admin/withdrawals')

@withdrawal_admin.route('/user-requests')
def user_withdrawal_requests():
    # You can add logic to fetch withdrawals here
    return render_template('admin/withdrawals/user_requests.html')


# Route for bulk withdrawal actions (placeholder)
@withdrawal_admin.route('/user-bulk')
def user_withdrawal_bulk():
    # Add logic for bulk withdrawal actions here
    return render_template('admin/withdrawals/user_bulk.html')


# Route for client withdrawal requests
@withdrawal_admin.route('/client-requests')
def client_withdrawal_requests():
    # Add logic for client withdrawal requests here
    return render_template('admin/withdrawals/client_requests.html')


# Route for client bulk withdrawal actions
@withdrawal_admin.route('/client-bulk')
def client_withdrawal_bulk():
    # Add logic for client bulk withdrawal actions here
    return render_template('admin/withdrawals/client_bulk.html')


# Route for withdrawal history
@withdrawal_admin.route('/history')
def withdrawal_history():
    # Add logic for withdrawal history here
    return render_template('admin/withdrawals/list.html')


# Route for withdrawal reports
@withdrawal_admin.route('/reports')
def withdrawal_reports():
    # Add logic for withdrawal reports here
    return render_template('admin/withdrawals/list.html')
