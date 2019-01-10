from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, \
IntegerField, DateField, SelectField, RadioField, FormField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email


class UpperForm(FlaskForm):
    ''' Group Form '''
    vendor = SelectField('Category', choices=[('Choice1', 'First'),('Choice2','Second'),('Choice3', 'Third')])
    delivery = RadioField('Delivery', choices=[('organization', 'Organization'),('customer', 'Customer')])
    purchase = StringField('Username', validators=[DataRequired()])
    reference = StringField('Username', validators=[DataRequired()])
    currentDate = DateField('Current Date', format='%m/%d/%y')
    deliveryDate = DateField('Delivery Date', format='%m/%d/%y')

class PurchaseForm(FlaskForm):
    submit = None

class LoginForm(FlaskForm):
    ''' Login Form '''
    username = StringField('Username', validators=[DataRequired()])
    pw = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class ProductForm(FlaskForm):
    ''' Product Items '''
    product = StringField('Product Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Choice1', 'First'),('Choice2','Second'),('Choice3', 'Third')])
    sku = StringField('SKU', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    currency = SelectField('Currency', choices=[('Choice1', 'First'),('Choice2','Second'),('Choice3', 'Third')])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    tags = StringField('Tags', validators=[])
    submit = SubmitField('Add Item')

class RegisterForm(FlaskForm):
    ''' Registers new users with the app '''
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    pw = PasswordField('Password', validators=[DataRequired()])
    pw2 = PasswordField('Repeat Password', validators=[DataRequired(),
    EqualTo('pw')])
    submit = SubmitField('Register')

    def validate_username(self, name):
        ''' validates if a user exists '''
        user = db.Users.find_one({'id':name.data})
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        ''' validates if a email exists '''
        email = db.Users.find_one({'id':email.data})
        if email is not None:
            raise ValidationError('Email is already in use.')
