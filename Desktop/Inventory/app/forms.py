from app import db
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, \
IntegerField, DateField, SelectField, RadioField, FormField, HiddenField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from markupsafe import Markup

def getGroups():
    groups = db.Groups.find()
    size = groups.count() - 1
    choices = []

    while size >= 0:
        choices.append((groups[size]['id'], groups[size]['name']))
        size -= 1

    if len(choices) == 0:
        return [('none', 'None')]
    return choices

def getVendor():
    vendor = db.Vendor.find()
    size = vendor.count() - 1
    choices = []

    while size >= 0:
        choices.append((vendor[size]['id'], vendor[size]['vendor']))
        size -= 1

    if len(choices) == 0:
        return [('none', 'None')]
    return choices

class BillingForm(FlaskForm):
    vendor = SelectField('Category', choices=getVendor())
    submit = None

class VendorForm(FlaskForm):
    vendor = StringField('Vendor Name')
    url = StringField('URL')
    submit = SubmitField('Add Vendor')

class GroupForm(FlaskForm):
    ''' Group Add Form '''
    type = RadioField('Type', choices=[('goods', 'Goods'),('service', 'Service')])
    name = StringField('Group Name')
    description = StringField('Description')
    unit = StringField('Unit')
    manufacturer = StringField('Manufacturer')
    tax = StringField('Tax')
    brand = StringField('Manufacturer')
    submit = SubmitField('Add Group')

class CategoryForm(FlaskForm):
    ''' Category Add Form '''
    name = StringField('Category Name')
    submit = SubmitField('Add Group')

class UpperForm(FlaskForm):
    ''' Group Form '''
    vendor = SelectField('Category', choices=[('Choice1', 'First'),('Choice2','Second'),('Choice3', 'Third')])
    delivery = RadioField('Delivery', choices=[('organization', 'Organization'),('customer', 'Customer')])
    purchase = StringField('Username', validators=[DataRequired()])
    reference = StringField('Username', validators=[DataRequired()])
    currentDate = DateField('Current Date', format='%m/%d/%y')
    deliveryDate = DateField('Delivery Date', format='%m/%d/%y')

class PurchaseForm(FlaskForm):
    ''' Purchase Form '''
    vendor = SelectField('Category', choices=getVendor())
    purchase = StringField('Purchase Order', validators=[DataRequired()])
    reference = StringField('Reference Order', validators=[DataRequired()])
    current_date = DateField('Current Date', format='%m/%d/%Y')
    delivery_date = DateField('Delivery Date', format='%m/%d/%Y')
    discount = StringField('Discount', validators=[DataRequired()])
    item_notes = StringField('Notes', validators=[DataRequired()])
    terms_notes = StringField('Terms & Conditions', validators=[DataRequired()])
    orders = StringField()
    submit_value = Markup('Submit form <i class="icon-paperplane ml-2"></i>')
    submit = SubmitField(submit_value)

class LoginForm(FlaskForm):
    ''' Login Form '''
    username = StringField('Username', validators=[DataRequired()])
    pw = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class ProductForm(FlaskForm):
    ''' Product Items '''
    product = StringField('Product Name', validators=[DataRequired()])
    category = SelectField('Category', choices=getGroups())
    #print(category)
    sku = StringField('SKU', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    currency = SelectField('Currency', choices=[('USD', '$'),('EURO','€'),('POUND', '£')])
    ###For Attributes by XLZ
    attr0 = StringField('Attribute', validators=[DataRequired()])
    options0 = StringField('Options', validators=[DataRequired()])
    attr1 = StringField('Attribute')
    options1 = StringField('Options')
    attr2 = StringField('Attribute')
    options2 = StringField('Options')
    ###For HiddenTag by XLZ
    hdfiles = HiddenField("HiddenFiles")

    url = StringField('URL')
    vendor = SelectField('Vendor', choices=getVendor())
    url = StringField('URL')
    submit = SubmitField('Add Item', render_kw={"class": "btn btn-primary btn-block"})

    def update_category(self):
       self.category.choices = getGroups()
       #self.category.default = getGroups()[0][id]

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
