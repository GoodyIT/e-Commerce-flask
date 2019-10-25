from app import db
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, PasswordField, TextAreaField, \
IntegerField, DateField, SelectField, RadioField, FormField, HiddenField, \
FileField, MultipleFileField, BooleanField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
from markupsafe import Markup
from werkzeug.utils import secure_filename

import os

def getGroups():
    groups = db.Groups.find()
    size = groups.count() - 1
    choices = [('','None')]
    while size >= 0:
        choices.append((groups[size]['id'], groups[size]['name']))
        size -= 1

    if len(choices) == 0:
        return [('', 'None')]
    return choices

def getSubgroups():
    groups = db.Groups.find()
    size = groups.count() - 1

    choices = []
    while size >= 0:
        if 'sub_group' in groups[size]:
            for subgroup in groups[size]['sub_group']:
                choices.append((subgroup, subgroup))
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

def getYears(min=2019, max=2039):
    choices = [('None','None')]
    while min <= max:
        choices.append((str(min),str(min)))
        min += 1
    return choices

class BillingForm(FlaskForm):
    vendor = SelectField('Category', choices=getVendor())
    submit = None

class VendorForm(FlaskForm):
    vendor = StringField('Vendor Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    submit = SubmitField('Add Vendor')

class GroupForm(FlaskForm):
    ''' Group Add Form '''
    type = RadioField('Type', choices=[
        ('GAMES', 'GAMES'),
        ('OFFICE', 'OFFICE'),
        ('ELECTRONICS', 'ELECTRONICS'),
        ('GEAR', 'GEAR'),
        ('COMPUTERS', 'COMPUTERS'),
        ('TOYS', 'TOYS'),
        ('ACCESSORIES', 'ACCESSORIES'),
        ('CUSTOM', 'CUSTOM')
    ])
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
    discount = StringField('Discount')
    item_notes = StringField('Notes')
    terms_notes = StringField('Terms & Conditions')
    orders = StringField()
    submit_value = Markup('Submit form <i class="icon-paperplane ml-2"></i>')
    submit = SubmitField(submit_value)

class StoreLoginForm(FlaskForm):
    ''' Store Login Form '''
    email = StringField('Email', validators=[DataRequired()])
    pw = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class StoreSignupForm(FlaskForm):
    ''' Store Signup Form '''
    first = StringField('First Name', validators=[DataRequired()])
    last = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    pw = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, name):
        ''' validates if a user exists '''
        user = db.Category.find_one({'id':name.data})
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        ''' validates if a email exists '''
        email = db.Category.find_one({'id':email.data})
        if email is not None:
            raise ValidationError('Email is already in use.')

class LoginForm(FlaskForm):
    ''' Login Form '''
    username = StringField('Username', validators=[DataRequired()])
    pw = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class ProductForm(FlaskForm):
    ''' Product Items '''
    product = StringField('Product Name', validators=[DataRequired()])
    category = SelectField('Category', choices=getGroups(), validators=[DataRequired()])
    subgroup = SelectField('SubGroup', choices=getSubgroups())
    summary = TextAreaField('Summary', validators=[DataRequired()])
    sku = StringField('SKU', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    imgImport = FileField('Image File', validators=[])
    addImport = MultipleFileField('Additional Images', validators=[])
    currency = SelectField('Currency', choices=[('USD', '$'),('EURO','€'),('POUND', '£')])
    attr0 = StringField('Attribute')
    options0 = StringField('Options')
    attr1 = StringField('Attribute')
    options1 = StringField('Options')
    attr2 = StringField('Attribute')
    options2 = StringField('Options')
    hdfiles = HiddenField("HiddenFiles")
    url = StringField('URL')
    vendor = SelectField('Vendor', choices=getVendor())
    url = StringField('URL')
    submit = SubmitField('Add Item', render_kw={"class": "btn btn-primary btn-block"})

    def update_category(self):
       #self.category.default = getGroups()[0][id]
       self.category.choices = getGroups()
       self.subgroup.choices = getSubgroups()

    def upload(self):
        form = ProductForm()
        if form.imgImport.data:
            f = form.imgImport.data
            curDirPath = os.path.dirname(os.path.realpath(__file__))
            uploadFolder = os.path.join(curDirPath, "uploads")
            filename = secure_filename(f.filename)
            impfilepath = os.path.join(uploadFolder, filename)
            f.save(impfilepath)
            return '../uploads/{}'.format(filename)

    def multiple_upload(self):
        form = ProductForm()
        if form.addImport.data:
            names = []
            f = form.imgImport.data
            add = form.addImport.data
            curDirPath = os.path.dirname(os.path.realpath(__file__))
            uploadFolder = os.path.join(curDirPath, "uploads")

            for x in add:
                filename = secure_filename(x.filename)
                impfilepath = os.path.join(uploadFolder, filename)
                imgLoc = "../uploads/{}".format(x.filename)
                names.append(imgLoc)
                x.save(impfilepath)
            return names

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

class UpdatePaymentsForm(FlaskForm):
    card = SelectField('Card', choices=[('None','None'),('visa', 'visa'),('discovery','discovery'),('mastercard', 'mastercard')])
    cardNumber = StringField('Card Number:', validators=[])
    cardName = StringField('Card Name:', validators=[] )
    cardYear = SelectField('Card Year', choices=getYears(2019, 2039))
    cardMonth = SelectField('Card Month', choices=[('None','None'),('01', '01'),('02','02'),('03', '03'),('04', '04'),('05','05'),('06', '06'),('07', '07'),('08','08'),('09', '09'),('10', '10'),('11','11'),('12', '12')])
    address = StringField('Billing Address', validators=[] )
    address2 = StringField('Address 2', validators=[] )
    city = StringField('City', validators=[] )
    state = SelectField('State', choices=getGroups() )
    zip = StringField('Zip', validators=[] )
    phone = StringField('Phone')
    submit = SubmitField('Update')

class EmailForm(FlaskForm):
    newsletter = BooleanField('Eloraus Newsletter', validators=[])
    deals = BooleanField('Eloraus Flash Deals', validators=[])
    rating = BooleanField('Product Rating', validators=[])
    seller = BooleanField('Seller Rating', validators=[])
    voting = BooleanField('Product Voting', validators=[])
    offers = BooleanField('Special Offers', validators=[])
    unsubscribe = BooleanField('Unsubscribe from all Email Notifications', validators=[])
    submit = SubmitField()

class TextForm(FlaskForm):
    phone = StringField('Number', validators=[])
    auto = BooleanField('Auto Notifications', validators=[])
    alert = BooleanField('Price Alert', validators=[])
    shipment = BooleanField('Shipment Notifications', validators=[])
    unsubscribe = BooleanField('Unsubscribe from all Email Notifications', validators=[])
    submit = SubmitField()

class SettingsForm(FlaskForm):
    first = StringField('First Name', validators=[])
    last = StringField('Last Name', validators=[])
    pw = PasswordField('Password', validators=[])
    submit = SubmitField('Update')

class CouponForm(FlaskForm):
    coupon = StringField('Coupon Code', validators=[])
    submit = SubmitField('Add Coupon')
