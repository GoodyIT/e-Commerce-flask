from app import app, db, login
from flask import render_template, json, url_for, flash, redirect, request, jsonify, g, Flask
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime as date
from .forms import RegisterForm, LoginForm, ProductForm, PurchaseForm
from .data import User
from .inventory import Warehouse


# load user
@login.user_loader
def load_user(username):
    user = db.Users.find_one({'id':username})
    if not user:
        return None
    return User(user['id'])

# Error handling
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# home page
@app.route('/')
@login_required
def home():
    products = db.Products.find()
    return render_template('index.html', title='Home Page', total=products)

# Purchase
@app.route('/purchase/items')
def post_purchase():
    if request.method == 'POST':
        print("++++++++++NEW REQUEST++++++++++++")
        print(request.data);
        return redirect(url_for('post_purchase'))
    return render_template('purchase.html', title='Purchase Order')

# Purchase
@app.route('/purchase')
@login_required
def purchase():
    form = PurchaseForm()
    if form.validate_on_submit():
        '''
        if form.validate_on_submit():
            new_item = {
                'order_id' : form.purchase.data,
                'reference_id' : form.reference.data,
                'order_date' : form.date.data,
                'delivery_date' : form.delivery.data,
            }
            db.Purchase.insert_one(new_item)
            flash('Item Added.')
        '''
        return redirect(url_for('purchase'))
    return render_template('purchase.html', title='Purchase Order', form=form)

# groups list
@app.route('/products/list')
@login_required
def groups_list():
    return render_template('groups_list.html', title='Groups List')
# groups
@app.route('/products/groups')
@login_required
def groups():
    return render_template('groups.html', title='Groups')

# products - add item
@app.route('/products/add', methods=['GET','POST'])
@login_required
def addItem():
    form = ProductForm()
    if form.validate_on_submit():
        print("+++++++++++SUBMITTED++++++++++++")
        new_item = {
            'id' : form.sku.data,
            'product' : form.product.data,
            'category' : form.category.data,
            'price' : form.price.data,
            'currency' : form.currency.data,
            'quantity' : form.quantity.data,
            'tags' : form.tags.data,
        }
        db.Products.insert_one(new_item)
        flash('New Item Added.')
        return redirect(url_for('products'))
    return render_template('add-item.html', title='Add Item', form=form)

# products
@app.route('/products', methods=['GET','POST'])
@login_required
def products():
    if request.method == 'POST':
        item = request.json
        db.Products.remove({'id':item['id']})
        response = app.response_class(
            response=json.dumps(item),
            status=200,
            mimetype='application/json'
        )
        return response

    table = db.Products.find()
    return render_template('products.html', title='Products', table=table)

# inventory - product orders
@app.route('/reports/activity-mail')
@login_required
def activity_mail():
    return render_template('activity-mail.html', title='Activity Mail')

# inventory - product orders
@app.route('/reports/activity-log')
@login_required
def activity_log():
    return render_template('activity-log.html', title='Activity Log')

# inventory - product orders
@app.route('/reports/purchases-orders')
@login_required
def purchases_orders():
    return render_template('purchases-orders.html', title='Purchases Orders')

# inventory - product receivable
@app.route('/reports/purchases-receivable')
@login_required
def purchases_receivable():
    return render_template('purchases-receivable.html', title='Purchases Details')

# inventory - product sales
@app.route('/reports/purchases-vendors')
@login_required
def purchases_vendors():
    return render_template('purchases-vendors.html', title='Purchases By Vendors')

# inventory - product sales
@app.route('/reports/purchases-items')
@login_required
def purchases_items():
    return render_template('purchases-items.html', title='Purchases by Items')

# inventory - purchase bills
@app.route('/reports/purchases-bills')
@login_required
def purchases_bills():
    return render_template('purchases-bills.html', title='Purchases by Bills')

# inventory - purchase balance
@app.route('/reports/purchases-balance')
@login_required
def purchases_balance():
    return render_template('purchases-balance.html', title='Vendor Balance')

# inventory - product sales
@app.route('/reports/purchases-payments')
@login_required
def purchases_payments():
    return render_template('purchases-payments.html', title='Purchases by Payments')

# inventory - product sales
@app.route('/reports/inventory-fifo')
@login_required
def inventory_fifo():
    return render_template('inventory-fifo.html', title='FIFO')

# inventory - product sales
@app.route('/reports/inventory-valuation')
@login_required
def inventory_valuation():
    return render_template('inventory-valuation.html', title='Inventory Valuation')

# inventory - product sales
@app.route('/reports/inventory-details')
@login_required
def inventory_details():
    return render_template('inventory-details.html', title='Inventory Details')

# inventory - product sales
@app.route('/reports/inventory-sales')
@login_required
def inventory_sales():
    return render_template('inventory-sales.html', title='Product Sales')

# inventory - order history
@app.route('/reports/inventory-purchases')
@login_required
def inventory_purchases():
    return render_template('inventory-purchases.html', title='Active Purchases')

# sales -
@app.route('/reports/sales-item')
@login_required
def sales_item():
    return render_template('sales-item.html', title='Sales Items')

# inventory - product sales
@app.route('/reports/salesman')
@login_required
def salesman():
    return render_template('salesman.html', title='Salesman')

# inventory - product sales
@app.route('/reports/sales-balance')
@login_required
def sales_balance():
    return render_template('sales-balance.html', title='Balance')

# sales - packing history
@app.route('/reports/sales-packing')
@login_required
def sales_packing():
    return render_template('sales-packing.html', title='Sales Packing')

# sales - payment history
@app.route('/reports/sales-payments')
@login_required
def sales_payments():
    return render_template('sales-payments.html', title='Sales Payments')

# sales - invoice history
@app.route('/reports/sales-customers')
@login_required
def sales_customers():
    return render_template('sales-customers.html', title='Sales Customer')

# sales - sales orders
@app.route('/reports/sales-orders')
@login_required
def sales_orders():
    return render_template('sales-orders.html', title='Sales Order')

# sales - sales product
@app.route('/reports/sales-invoice')
@login_required
def sales_invoice():
    return render_template('sales-invoice.html', title='Sales Invoices')

# integrations
@app.route('/integrations')
@login_required
def integrations():
    return render_template('integrations.html', title='Integrations')

# reports
@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html', title='Report')

# billing
@app.route('/billing')
@login_required
def billing():
    return render_template('billing.html', title='Billing')

# exports
@app.route('/files')
@login_required
def files():
    return render_template('files.html', title='Files')

# contacts
@app.route('/contacts')
@login_required
def contacts():
    return render_template('contacts.html', title='Contacts')

# Orders
@app.route('/orders', methods=['GET','POST'])
@login_required
def orders():
    if request.method == 'POST':
        item = request.json
        new_order = db.Queue.find_one({'order_id':item['id']})
        db.Queue.remove({'order_id':item['id']})
        db.Orders.insert_one(new_order)

        response = app.response_class(
            response=json.dumps(item),
            status=200,
            mimetype='application/json'
        )
        return response

    table = db.Orders.find()
    return render_template('orders.html', title='Queue', table=table)

# Queue
@app.route('/queue', methods=['GET','POST'])
@login_required
def queue():
    # current = db.Queue.find()
    if request.method == 'POST':
        item = request.json
        db.Queue.remove({'order_id':item['id']})
        response = app.response_class(
            response=json.dumps(item),
            status=200,
            mimetype='application/json'
        )
        return response

    queue = db.Queue.find()
    return render_template('queue.html', title='Queue', queue=queue)

# signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = {
            'id': form.username.data,
            'name':form.name.data,
            'uid': User.setUID(),
            'email':form.email.data,
            'pw': User.setHash(form.pw.data),
        }
        db.Users.insert_one(new_user)
        flash('Congratulations {}, you are now a registered user!'.format(form.name.data))
        return redirect(url_for('home'))
    return render_template('signup.html', title='Register', form=form)

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.Users.find_one({'id':form.username.data})
        if user != None and User.checkPassword(user['pw'], form.pw.data):
            verify = User(user['id'])
            login_user(verify)
            return redirect(url_for('home'))
        flash('Invalid Username or Password. Please try again.')
        return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form)

# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))