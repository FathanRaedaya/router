''' * forms.py defines Flask-WTF forms used for various user interactions within Router.
 *
 * * Login (LoginForm): Collects username and password for authentication.
 * * Registration (RegisterForm): Gathers user information for creating a new account (username, email, first/last name, password).
 * * Payment (PaymentForm): Collects credit/debit card details, billing address, and associated information for processing payments.
 * * Route Upload (UploadForm): Allows users to upload route files (GPX), optionally add a description, and select friends to share with.
 * * Change Username (ChangeUsernameForm): Enables users to update their username, including validation for matching entries and unique usernames.
 * * Change Password (ChangePasswordForm): Provides functionality for users to securely change their password. 
 '''

from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, FileField, PasswordField,\
    TextAreaField, EmailField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length
import datetime

from app.models import User
from .countries import countries


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=1, max=100)])
    pw = PasswordField('Password',
                       validators=[DataRequired(), Length(min=1, max=100)])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=1, max=100)])
    email = EmailField('Email',
                       validators=[DataRequired(), Length(min=1, max=100)])
    fName = StringField('First Name',
                        validators=[DataRequired(), Length(min=1, max=100)])
    lName = StringField('Last Name',
                        validators=[DataRequired(), Length(min=1, max=100)])
    pw = PasswordField('Password',
                       validators=[DataRequired(), Length(min=6, max=100)])
    pw2 = PasswordField('Confirm Password',
                        validators=[DataRequired(), Length(min=6, max=100)])
    submit = SubmitField('Register')


class PaymentForm(FlaskForm):
    fName = StringField('First Name',
                        validators=[DataRequired(), Length(min=1, max=100)])
    lName = StringField('Last Name',
                        validators=[DataRequired(), Length(min=1, max=100)])
    cardNum = StringField('Card Number',
                          validators=[DataRequired(), Length(min=1, max=100)])
    expirationM = SelectField('Expiration Month',
                              validators=[DataRequired(), Length(min=1,
                                                                 max=100)],
                              choices=[m for m in
                                       range(datetime.date.today().month, 13)])
    expirationY = SelectField('Expiration Year',
                              validators=[DataRequired(),
                                          Length(min=1, max=100)],
                              choices=[y for y in range
                                       (datetime.date.today().year, 2041)])
    cvv = StringField('CVV',
                      validators=[DataRequired(), Length(min=1, max=100)])
    country = SelectField('Country',
                          validators=[DataRequired(), Length(min=1, max=100)],
                          choices=[c[1] for c in countries])
    city = StringField('City',
                       validators=[DataRequired(), Length(min=1, max=100)])
    stAddr = StringField('Street Address',
                         validators=[DataRequired(), Length(min=1, max=100)])
    stAddr2 = StringField('Street Address 2',
                          validators=[Length(min=1, max=100)])
    pc = StringField('Post Code',
                     validators=[DataRequired(), Length(min=6, max=8)])
    submit = SubmitField('Pay')


class UploadForm(FlaskForm):
    route = FileField('Route', validators=[DataRequired()])
    description = TextAreaField('Description')
    share = SelectField("Friend Selection", validators=[DataRequired()])
    submit = SubmitField('Submit')


class ChangeUsernameForm(FlaskForm):
    username1 = StringField('Username', validators=[Length(min=1, max=100)])
    username2 = StringField('Confirm Username',
                            validators=[Length(min=1, max=100)])
    submit = SubmitField('Change Username')

    def validate_username1(self, username1):
        if self.username1.data != self.username2.data:
            raise ValidationError('Usernames do not match')
        if User.query.filter_by(username=self.username1.data).first():
            raise ValidationError('Username already taken')
        if self.username1.data == current_user.username:
            raise ValidationError('New username cannot be the \
                                  same as the current username')


class ChangePasswordForm(FlaskForm):
    pw = PasswordField('Password', validators=[Length(min=6, max=100)])
    pw2 = PasswordField('Confirm Password',
                        validators=[Length(min=6, max=100)])
    submit = SubmitField('Change Password')

    def validate_pw(self, pw):
        if self.pw.data != self.pw2.data:
            raise ValidationError('Passwords do not match')
        if current_user.verify_pw(self.pw.data):
            raise ValidationError('Password does not match2')
