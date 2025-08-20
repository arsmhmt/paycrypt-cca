from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DecimalField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange

class ClientLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class ClientForm(FlaskForm):
    # Basic Information
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=128)])
    client_type = SelectField('Client Type', choices=[('COMPANY', 'Company'), ('INDIVIDUAL', 'Individual')], validators=[DataRequired()])
    name = StringField('Contact Name', validators=[Optional(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=128)])
    phone = StringField('Phone', validators=[Optional(), Length(max=32)])
    website = StringField('Website', validators=[Optional(), Length(max=128)])

    # Login Credentials
    username = StringField('Username', validators=[Optional(), Length(max=64)])
    password = PasswordField('Password', validators=[Optional(), Length(max=128)])
    new_password = PasswordField('New Password', validators=[Optional(), Length(max=128)])
    auto_generate_password = BooleanField('Auto-generate password')

    # Address Information
    address = StringField('Address', validators=[Optional(), Length(max=256)])
    city = StringField('City', validators=[Optional(), Length(max=64)])
    country = StringField('Country', validators=[Optional(), Length(max=64)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=32)])

    # Business Information
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=64)])
    vat_number = StringField('VAT Number', validators=[Optional(), Length(max=64)])
    registration_number = StringField('Registration Number', validators=[Optional(), Length(max=64)])

    # Package and Status Management
    package_id = SelectField('Package', coerce=int, validators=[Optional()])
    client_status = SelectField('Client Status', choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], validators=[Optional()])
    is_active = BooleanField('Is Active')
    is_verified = BooleanField('Is Verified')

    # Account Balance Management
    balance = DecimalField('Balance', validators=[Optional(), NumberRange(min=0)], places=8, default=0)
    commission_balance = DecimalField('Commission Balance', validators=[Optional(), NumberRange(min=0)], places=8, default=0)

    # Additional Contact Information
    contact_person = StringField('Contact Person', validators=[Optional(), Length(max=64)])
    contact_email = StringField('Contact Email', validators=[Optional(), Email(), Length(max=128)])
    contact_phone = StringField('Contact Phone', validators=[Optional(), Length(max=32)])

    # Technical Settings
    rate_limit = IntegerField('API Rate Limit', validators=[Optional(), NumberRange(min=0)], default=0)
    theme_color = StringField('Theme Color', validators=[Optional(), Length(max=16)])

    # API Management
    api_key_enabled = BooleanField('API Key Enabled')
    auto_generate_api_key = BooleanField('Auto-generate API Key')
    webhook_url = StringField('Webhook URL', validators=[Optional(), Length(max=256)])

    # Commission Settings
    deposit_commission_rate = DecimalField('Deposit Commission Rate', validators=[Optional(), NumberRange(min=0, max=100)], places=2, default=0)
    withdrawal_commission_rate = DecimalField('Withdrawal Commission Rate', validators=[Optional(), NumberRange(min=0, max=100)], places=2, default=0)

    # Notes
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1024)])

    submit = SubmitField('Save')
