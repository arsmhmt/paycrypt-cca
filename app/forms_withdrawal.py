from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class WithdrawalRequestForm(FlaskForm):
    currency = SelectField('Currency', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0.0001)], places=8)
    user_wallet_address = StringField('Wallet Address', validators=[DataRequired(), Length(max=128)])
    memo = StringField('Memo/Tag (optional)', validators=[Optional(), Length(max=64)])
    note = TextAreaField('Note (optional)', validators=[Optional(), Length(max=256)])
    submit = SubmitField('Request Withdrawal')
