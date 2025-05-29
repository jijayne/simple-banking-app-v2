from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, RadioField, SelectField, HiddenField
from wtforms.validators import (
    DataRequired, Email, EqualTo, ValidationError, NumberRange, Optional, Length, Regexp
)
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        
        user = User.query.filter_by(username=self.username.data).first()
        if user is None or not user.check_password(self.password.data):
            self.username.errors.append('Invalid username or password')
            return False
        
        if user.status != 'active':
            self.username.errors.append('Account is not active')
            return False
        
        return True

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Length(min=4, max=20),
            Regexp(
                r'^[A-Za-z0-9_]{4,20}$',
                message="Username must be 4-20 characters and contain only letters, numbers, or underscores."
            )
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message="Invalid email address."),
            Length(max=120)
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8, max=128),
            Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+\-=\[\]{};\'\":\\|,.<>\/?]{8,}$',
                message="Password must be at least 8 characters, include a letter and a number."
            )
        ]
    )
    password2 = PasswordField(
        'Repeat Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.'),
            Length(min=8, max=128)
        ]
    )
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate(self, extra_validators=None):
        return super().validate(extra_validators)

class TransferForm(FlaskForm):
    transfer_type = RadioField('Transfer Type', 
                              choices=[('username', 'By Username'), ('account', 'By Account Number')],
                              default='username')
    recipient_username = StringField('Recipient Username', validators=[Optional()])
    recipient_account = StringField('Recipient Account Number', validators=[Optional()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01, message="Amount must be greater than 0")])
    submit = SubmitField('Transfer')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        
        if self.transfer_type.data == 'username':
            if not self.recipient_username.data:
                self.recipient_username.errors.append('Recipient username is required')
                return False
        else:
            if not self.recipient_account.data:
                self.recipient_account.errors.append('Recipient account number is required')
                return False
        
        return True

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        
        user = User.query.filter_by(email=self.email.data).first()
        if user is None:
            self.email.errors.append('Email address not found')
            return False
        
        return True

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class DepositForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    submit = SubmitField('Deposit')

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    firstname = StringField('First Name', validators=[Optional()])
    lastname = StringField('Last Name', validators=[Optional()])
    phone = StringField('Phone', validators=[Optional()])
    address_line = StringField('Address', validators=[Optional()])
    region_code = SelectField('Region', choices=[], validators=[Optional()])
    province_code = SelectField('Province', choices=[], validators=[Optional()])
    city_code = SelectField('City', choices=[], validators=[Optional()])
    barangay_code = SelectField('Barangay', choices=[], validators=[Optional()])
    postal_code = StringField('Postal Code', validators=[Optional()])
    status = SelectField('Status', choices=[('active', 'Active'), ('pending', 'Pending'), ('deactivated', 'Deactivated')])
    submit = SubmitField('Update User')

class ConfirmTransferForm(FlaskForm):
    confirm = SubmitField('Confirm Transfer')
    cancel = SubmitField('Cancel')