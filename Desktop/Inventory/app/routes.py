from app import app, db, login
from flask import render_template, json, url_for, flash, redirect, request, jsonify, g, Flask
from flask_login import login_user, logout_user, login_required, current_user
from uuid import uuid4 as uid
from datetime import datetime as date
from werkzeug.utils import secure_filename
from .forms import RegisterForm, LoginForm, ProductForm, PurchaseForm, GroupForm, VendorForm, BillingForm
from .data import User
from .inventory import Warehouse
import json
import os


#app = Flask(__name__)

def allowed_file(filename):
    ''' method for choosing form file path '''
    curDirPath = os.path.dirname(os.path.realpath(__file__))
    UPLOAD_FOLDER = os.path.join(curDirPath,"uploads")
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def getGroups():
    ''' SelectField method for getting group list '''
    groups = db.Groups.find()
    size = groups.count() - 1
    choices = {}

    while size >= 0:
        choices[ groups[size]['id'] ] = groups[size]['name']
        size -= 1

    if len(choices) == 0:
        return {'none':'None'}
    return choices

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

# Internal handling
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# home page
@app.route('/')
@login_required
def home():
    products = db.Products.find()

    return render_template(
        'index.html', 
        title='Home Page', 
        total=products, 
    )

# Get analytics
@app.route('/analytics', methods=['POST'])
@login_required
def get_analytics():
    requestData = json.loads(request.data)
    print(requestData)
    if (requestData['type'] == 'init'):
        analyticsByState = db.Orders.aggregate([
            {
                "$group" : {
                    "_id":"$state", 
                    "price": { 
                        "$sum": { 
                            "$multiply": [ "$price", "$quantity" ]
                        }
                    },
                    "quantity": { 
                        "$sum": "$quantity"
                    },
                    "count": { "$sum": 1 }
                }
            },
            { "$sort": { "_id": 1} }
        ])

        analyticsByYearly = db.Orders.aggregate([
            {
                "$group": 
                {
                    "_id": { "year": { "$year": "$date" } },
                    "price": { 
                        "$sum": { 
                            "$multiply": [ "$price", "$quantity" ]
                        } 
                    },
                    "quantity": { 
                        "$sum": "$quantity"
                    },
                    "count": { "$sum": 1 }
                }
            },
            { "$sort": { "_id": 1} }
        ])
        analyticsByItem = db.Orders.aggregate([
            {
                "$group": 
                {
                    "_id": "$item_id",
                    "price": { 
                        "$sum": { 
                            "$multiply": [ "$price", "$quantity" ]
                        } 
                    },
                    "quantity": { 
                        "$sum": "$quantity"
                    },
                    "count": { "$sum": 1 }
                }
            }
        ])
        analytics = db.Orders.aggregate([
            {
                "$group": {
                    "_id": "1",
                    "price": { 
                        "$sum": { 
                            "$multiply": [ "$price", "$quantity" ]
                        } 
                    },
                    "quantity": { 
                        "$sum": "$quantity"
                    },
                    "count": { "$sum": 1 }
                }
            }
        ])
        return jsonify({
            "analyticsByYearly": list(analyticsByYearly),
            "analyticsByState": list(analyticsByState),
            "analyticsByItem": list(analyticsByItem),
            "analytics": list(analytics)[0]
        })
    if (requestData['type'] == 'by_daily'):
        analyticsByDaily = db.Orders.aggregate([
            {
                "$group": 
                {
                    "_id": { "year": { "$year": "$date" }, "day": { "$dayOfYear": "$date"} },
                    "price": { 
                        "$sum": { 
                            "$multiply": [ "$price", "$quantity" ]
                        } 
                    },
                    "quantity": { 
                        "$sum": "$quantity"
                    },
                    "count": { "$sum": 1 }
                }
            },
            { "$sort": { "_id": 1} }
        ])
        return jsonify({
            "analyticsByDaily": list(analyticsByDaily)
        })
    if (requestData['type'] == 'by_weekly'):
        analyticsByWeekly = db.Orders.aggregate([
            {
                "$group": 
                {
                    "_id": { "year": { "$year": "$date" }, "week": { "$week": "$date"} },
                    "price": { 
                        "$sum": { 
                            "$multiply": [ "$price", "$quantity" ]
                        } 
                    },
                    "quantity": { 
                        "$sum": "$quantity"
                    },
                    "count": { "$sum": 1 }
                }
            },
            { "$sort": { "_id": 1} }
        ])
        return jsonify({
            "analyticsByWeekly": list(analyticsByWeekly)
        })
    if (requestData['type'] == 'by_monthly'):
        analyticsByMonthly = db.Orders.aggregate([
            {
                "$group": 
                {
                    "_id": { "year": { "$year": "$date" }, "month": { "$month": "$date"} },
                    "price": { 
                        "$sum": { 
                            "$multiply": [ "$price", "$quantity" ]
                        } 
                    },
                    "quantity": { 
                        "$sum": "$quantity"
                    },
                    "count": { "$sum": 1 }
                }
            },
            { "$sort": { "_id": 1} }
        ])
        return jsonify({
            "analyticsByMonthly": list(analyticsByMonthly)
        })
    if (requestData['type'] == 'by_yearly'):
        analyticsByYearly = db.Orders.aggregate([
            {
                "$group": 
                {
                    "_id": { "year": { "$year": "$date" } },
                    "price": { 
                        "$sum": { 
                            "$multiply": [ "$price", "$quantity" ]
                        } 
                    },
                    "quantity": { 
                        "$sum": "$quantity"
                    },
                    "count": { "$sum": 1 }
                }
            },
            { "$sort": { "_id": 1} }
        ])
        return jsonify({
            "analyticsByYearly": list(analyticsByYearly)
        })
    return jsonify({})
    
#store - games
@app.route('/store/games')
def games():
    return render_template('grid-games.html', title='Games')

#store - office
@app.route('/store/office')
def office():
    return render_template('grid-games.html', title='Office')

#store - electronics
@app.route('/store/electronics')
def electronics():
    return render_template('grid-electronics.html', title='Electronics')

#store - gear
@app.route('/store/gear')
def gear():
    return render_template('grid-gear.html', title='Gear')

#store - computers
@app.route('/store/computers')
def computers():
    return render_template('grid-computers.html', title='Computers')

#store - toys
@app.route('/store/toys')
def toys():
    return render_template('grid-toys.html', title='Toys')

#store - accessories
@app.route('/store/accessories')
def accessories():
    return render_template('grid-accessories.html', title='Accessories')

#store
@app.route('/store')
def store():
    return render_template('store.html', title='Store')

# shipping
@app.route('/shipping')
@login_required
def shipping():
    orders = db.Orders.find()
    c = 0
    current = {}

    while c < orders.count():
        if orders[c]['item_id'] in current:
            current[orders[c]['item_id']] += 1
        else:
            current[orders[c]['item_id']] = 1
        c += 1
    return render_template('shipping.html', title='Shipping', orders=current)

# Purchase
@app.route('/purchase/items')
def post_purchase():
    if request.method == 'POST':
        print("++++++++++NEW REQUEST++++++++++++")
        print(request.data)
        return redirect(url_for('post_purchase'))
    return render_template('purchase.html', title='Purchase Order')

# Purchase
@app.route('/purchase', methods=['GET','POST'])
@login_required
def purchase():
    form = PurchaseForm()
    if form.validate_on_submit():
        orderCells = form.orders.data.split(',')
        orders = []
        for x in range(0, len(orderCells), 6):
            orders.append({
                "Item Details"  : orderCells[x],
                "League"        : orderCells[x+1],
                "Quantity"      : orderCells[x+2],
                "Rate"          : orderCells[x+3],
                "Tax"           : orderCells[x+4],
                "Amount"        : orderCells[x+5],
            })
        new_item = {
            'vendor'        : form.vendor.data,
            'order_id'      : form.purchase.data,
            'reference_id'  : form.reference.data,
            'order_date'    : form.current_date.data.isoformat(),
            'delivery_date' : form.delivery_date.data.isoformat(),
            'orders'        : orders,
            'discount'      : form.discount.data,
            'notes'         : form.item_notes.data,
            'terms'         : form.terms_notes.data
        }
        print(new_item)
        db.Purchase.insert_one(new_item)
        flash('Item Added.')

        return redirect(url_for('purchase'))
    return render_template('purchase.html', title='Purchase Order', form=form)

# Purchase
@app.route('/bills')
@login_required
def bills():
    form = BillingForm()
    if form.validate_on_submit():
        return redirect(url_for('bills'))
    return render_template('bills.html', title='Billing', form=form)

# groups add
@app.route('/groups/add', methods=['GET','POST'])
@login_required
def groups_add():
    form = GroupForm()
    if form.validate_on_submit():
        new_item = {
            'id' : str(uid()),
            'type' : form.type.data,
            'name' : form.name.data,
            'description' : form.description.data,
            'unit' : form.unit.data,
            'manufacturer' : form.manufacturer.data,
            'tax' : form.tax.data,
            'brand' : form.brand.data,
            'total' : 0
        }
        db.Groups.insert_one(new_item)
        flash('New Group Added.')
        return redirect(url_for('groups'))
    return render_template('groups-add.html', title='Groups', form=form)

# groups
@app.route('/groups')
@login_required
def groups():
    groups = db.Groups.find()
    return render_template('groups.html', title='Groups', groups=groups)

# groups list
@app.route('/groups/<name>', methods=['GET','POST'])
@login_required
def groups_list(name):
    if request.method == 'POST':
        #print("++++++++++NEW REQUEST++++++++++++ pid: "+request.form.get("pid"))

        update_item = {
            'product' : request.form.get("pname"),
            'sku' : request.form.get("sku"),
            #'images' : images,
            'category' : request.form.get("cate"),
            'price' : request.form.get("price"),
            'currency' : request.form.get("curr"),
            #'attributes' : attrs,
            'vendor' : request.form.get("vendor"),
            'url' : request.form.get("url"),
        }
        ## Check attributes
        attrs = {}
        if request.form.get('attr0') :
            if request.form.get('attr0') != "" :
                attrs[request.form.get('attr0')] = request.form.get('options0')
        if request.form.get('attr1') :
            if request.form.get('attr1') != "" :
                attrs[request.form.get('attr1')] = request.form.get('options1')
        if request.form.get('attr2') :
            if request.form.get('attr2') != "" :
                attrs[request.form.get('attr2')] = request.form.get('options2')
        if bool(attrs):
            update_item['attributes'] = attrs
        print(update_item);

        db.Products.update_one({"id": request.form.get("pid")},{"$set":update_item},upsert=True)
        #return redirect(url_for('groups_list',name=name))

    try:
        group = db.Groups.find({'name':str(name)})
        #print("-------------------------- group: ",group[0]['id'])
        items = db.Products.find({'category':group[0]['id']})
        if items.count() == 0:
            flash("Product Does Not Exist")
            return redirect(url_for('addItem'))
        #print( items.__dict__ )        print(items[0])
    except TypeError:
        flash("Group Does Not Exist")
        return redirect(url_for('groups'))
    if request.method == 'GET':
        CURRENCIES=[('USD', '$'),('EURO','€'),('POUND', '£')]
    return render_template('groups-list.html', title='Groups List', items=items, cates=getGroups(), currs=CURRENCIES)

# ajax request :XLZ
@app.route('/getProduct', methods=['POST'])
@login_required
def getProduct():
    if request.method == 'POST':
        item = request.json
        print("++++++++++NEW REQUEST++++++++++++ item: ", item)
        prdt = db.Products.find_one({'id':item['pid']})

        return jsonify(id=prdt['id'], product=prdt['product'], sku=prdt['sku'], #'images' : prdt['images'],
            category=prdt['category'], price=prdt['price'], currency=prdt['currency'],
            attributes=prdt['attributes'], vendor=prdt['vendor'], url=prdt['url'])

# vendor
@app.route('/products/vendor', methods=['GET','POST'])
@login_required
def vendor():
    form = VendorForm()
    if form.validate_on_submit():
        vendor = {
            'id' : str(uid()),
            'vendor' : form.vendor.data,
            'url' : form.url.data
        }
        db.Vendor.insert_one(vendor)
        flash('New Vendor Added.')
        return redirect(url_for('vendor'))
    return render_template('vendor.html', title='Vendor', form=form)

# products - add item
@app.route('/products/add', methods=['GET','POST'])
@login_required
def addItem():
    form = ProductForm()
    form.update_category()
    file_urls = []
    if(request.method == 'POST') and 'photos' in request.files:
        print("\n routes | addItem --- POST : ||||||| ----------------------------\n")
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            if file.filename == '':
                flash('No selected file')
            imgfilepath = ""
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                imgfilepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(imgfilepath)
                # append image urls
                file_urls.append(imgfilepath)
        strjson = ",".join(file_urls)
        #print("------strjson: "+strjson)
        return jsonify(target_file=strjson)

    if form.validate_on_submit():
        # add new vendor
        vendor = ""
        if form.vendor.data != "none":
            vendor = form.vendor.data
            '''
            new_vendor = {
                'id' : str(uid()),
                'vendor' : vendor,
                'url' : form.url.data,
            }
            db.Vendor.insert_one(new_vendor)
            '''

        # add new product
        attrs = {form.attr0.data:form.options0.data}
        if form.attr1.data != "":
            attrs[form.attr1.data] = form.options1.data
        if form.attr2.data != "":
            attrs[form.attr2.data] = form.options2.data
        images = form.hdfiles.data
        #images = images.split(",")
        print("\n routes | addItem: ----------------------------")
        print(attrs)

        new_item = {
            'id' : str(uid()),
            'product' : form.product.data,
            'sku' : form.sku.data,
            'images' : images,
            'category' : form.category.data,
            'price' : form.price.data,
            'currency' : form.currency.data,
            'attributes' : attrs,
            'vendor' : vendor,
            'url' : form.url.data,
        }
        db.Products.insert_one(new_item)

        # update Groups inventory count
        current = db.Groups.find_one({'id': form.category.data})
        db.Groups.update_one(current,{"$set":{'total': current['total']+1}})

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
    print("++++++++++      login     +++++++++++")
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
