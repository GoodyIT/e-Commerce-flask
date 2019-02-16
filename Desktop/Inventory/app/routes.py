from app import app, db, login
from flask import render_template, json, url_for, flash, redirect, request, jsonify, g, Flask, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from uuid import uuid4 as uid
from datetime import datetime as date
from werkzeug.utils import secure_filename
from .forms import RegisterForm, LoginForm, ProductForm, PurchaseForm, GroupForm, VendorForm, BillingForm
from .data import User
from .inventory import Warehouse

import json
import os
import math
import random, pandas
from datetime import datetime
import csv
import pandas as pd #pip install pandas==0.16.1

from .zincapi_communication import post_shipping_request, post_cancellation_request

#app = Flask(__name__)
def _removeNewLine(input):
    ''' Removes \n from string elements '''
    if input.endswith('\n'):
        return input[0:len(input)-1]
    return input

def _getCity():
    ''' Returns a City from CSV '''
    df = pandas.read_csv(os.path.dirname(__file__) + '/../uscities.csv')
    return df['city'][random.randint(0,len(df['city']))]

def _getState():
    ''' Returns a City from CSV '''
    df = pandas.read_csv(os.path.dirname(__file__) + '/../uscities.csv')
    return df['state_id'][random.randint(0,len(df['state_id']))]

def _getZip():
    ''' Returns a City from CSV '''
    df = pandas.read_csv(os.path.dirname(__file__) + '/../uscities.csv')
    return df['zips'][random.randint(0,len(df['zips']))]

def _street():
    ''' Generates a address based around called names from streetNames.txt
    file '''
    ENDING = ['court', 'street', 'grove', 'avenue', 'place']
    NUMBER = random.randint(1, 5000)
    names = None

    with open(os.path.dirname(__file__) + '/../streetNames.txt') as f:
        names = f.readlines()
    choice = random.choice(names)
    return '{} {} {}'.format(str(NUMBER), _removeNewLine(choice), random.choice(ENDING))


curDirPath = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = os.path.join(curDirPath,"uploads")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
CURRENCIES = [('USD', '$'),('EURO','€'),('POUND', '£')]

BREAD_CRUMB = {'Signup':['Sign Up','signup'], 'Login':['Login','login'],
'Dashboard':['Dashboard','home'], 'Queue':['Queue','queue'],
'Reports':['Reports','reports'], 'Products':['Products','products'],
'Orders':['Orders','orders'], 'Shipping':['Shipping','Contacts']}

def allowed_file(filename):
    ''' method for choosing form file path '''
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

def getCategory():
    ''' SelectField method for getting category list '''
    categories = db.Category.find()
    size = categories.count() - 1
    choices = {}

    while size >= 0:
        choices[ categories[size]['id'] ] = categories[size]['name']
        size -= 1

    if len(choices) == 0:
        return {'none':'None'}
    return choices

def getVendors():
    ''' SelectField method for getting vendor list '''
    vendors = db.Vendor.find()
    size = vendors.count() - 1
    choices = {}

    while size >= 0:
        choices[ vendors[size]['id'] ] = vendors[size]['name']
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
        breadCrumb=BREAD_CRUMB['Dashboard'][0],
        uname=current_user.get_id(), 
        title='Home Page', 
        total=products
        )

# Get analytics
@app.route('/analytics', methods=['POST'])
@login_required
def get_analytics():
    requestData = json.loads(request.data)
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
                    #"_id": { "year": { "$year": "$date" } },
                    "_id": { "year": { "$substr": ["$date", 0, 4] } },
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
        analyticsByGroup = db.Orders.aggregate([
            {
                "$group":
                {
                    "_id": "$group_id",
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
            {
                "$lookup":
                {
                    "from": "Groups",
                    "localField": "_id",
                    "foreignField": "id",
                    "as": "group"
                }
            }
        ])

        analyticsByGroupArray = []
        for x in analyticsByGroup:
            if len(x['group']) > 0:
                analyticsByGroupArray.append({'group': x['group'][0]['name'], 'quantity': x['quantity']})
        totalQuantityAndCost = db.Orders.aggregate([
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
        totalQuantityAndCostArray = list(totalQuantityAndCost)
        packedOrderCount    = db.Queue.count_documents({})
        shippedOrderCount   = db.Orders.count_documents({"ship_id": None})
        deliveredOrderCount = db.Orders.count_documents({"$and": [{"ship_id": {"$ne": None}}, {"invoice_id": None}]})
        invoicedOrderCount  = db.Orders.count_documents({"$and": [{"ship_id": {"$ne": None}}, {"invoice_id": {"$ne": None}}]})
        return jsonify({
            "analyticsByYearly"   : list(analyticsByYearly),
            "analyticsByState"    : list(analyticsByState),
            "analyticsByGroup"    : analyticsByGroupArray,
            "totalCost"           : totalQuantityAndCostArray[0]['price'],
            "totalQuantity"       : totalQuantityAndCostArray[0]['quantity'],
            "packedOrderCount"    : packedOrderCount,
            "shippedOrderCount"   : shippedOrderCount,
            "deliveredOrderCount" : deliveredOrderCount,
            "invoicedOrderCount"  : invoicedOrderCount
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
    if (requestData['type'] == 'by_state'):
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
        return jsonify({
            "analyticsByState": list(analyticsByState)
        })
    if (requestData['type'] == 'by_country'):
        analyticsByCountry = db.Orders.aggregate([
            {
                "$group" : {
                    "_id":"$country",
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
            "analyticsByCountry": list(analyticsByCountry)
        })
    return jsonify({})
    
#store - games
@app.route('/games')
def games1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('games', gid=groupId, subgroup=subGroup, page=page))
@app.route('/store/games')
def games():
    groupId   = request.args.get("gid")
    subGroup  = request.args.get("subgroup")
    page      = request.args.get("page")
    if groupId is None:
        groupId='ALL'
    if subGroup is None:
        subGroup = 'ALL'
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    if groupId == 'ALL' and subGroup == 'ALL':
        products = db.Products.find({"category_type": "GAMES"}).skip((int(page)-1)*8).limit(8)
    else: 
        if groupId != 'ALL' and subGroup == 'ALL':
            products = db.Products.find({"category": groupId}).skip((int(page)-1)*8).limit(8)
        else:
            products = db.Products.find({"category": groupId, "subgroup": subGroup}).skip((int(page)-1)*8).limit(8)
    productArray = list(products)
    pageCount = math.ceil(products.count()/8)
    return render_template(
        'grid-games.html', 
        title='Games', 
        groups=groupsList, 
        products=productArray, 
        activeGroupId=groupId, 
        activeSubGroup=subGroup, 
        pageCount=pageCount,
        currentPage=page
    )

#store - office
@app.route('/office')
def office1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('office', gid=groupId, subgroup=subGroup, page=page))
@app.route('/store/office')
def office():
    groupId   = request.args.get("gid")
    subGroup  = request.args.get("subgroup")
    page      = request.args.get("page")
    if groupId is None:
        groupId='ALL'
    if subGroup is None:
        subGroup = 'ALL'
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    if groupId == 'ALL' and subGroup == 'ALL':
        products = db.Products.find({"category_type": "OFFICE"}).skip((int(page)-1)*8).limit(8)
    else: 
        if groupId != 'ALL' and subGroup == 'ALL':
            products = db.Products.find({"category": groupId}).skip((int(page)-1)*8).limit(8)
        else:
            products = db.Products.find({"category": groupId, "subgroup": subGroup}).skip((int(page)-1)*8).limit(8)
    productArray = list(products)
    pageCount = math.ceil(products.count()/8)
    return render_template(
        'grid-office.html', 
        title='Office', 
        groups=groupsList, 
        products=productArray, 
        activeGroupId=groupId, 
        activeSubGroup=subGroup, 
        pageCount=pageCount,
        currentPage=page
    )

#store - electronics
@app.route('/electronics')
def electrnoics1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('electronics', gid=groupId, subgroup=subGroup, page=page))
@app.route('/store/electronics')
def electronics():
    groupId   = request.args.get("gid")
    subGroup  = request.args.get("subgroup")
    page      = request.args.get("page")
    if groupId is None:
        groupId='ALL'
    if subGroup is None:
        subGroup = 'ALL'
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    if groupId == 'ALL' and subGroup == 'ALL':
        products = db.Products.find({"category_type": "ELECTRONICS"}).skip((int(page)-1)*8).limit(8)
    else: 
        if groupId != 'ALL' and subGroup == 'ALL':
            products = db.Products.find({"category": groupId}).skip((int(page)-1)*8).limit(8)
        else:
            products = db.Products.find({"category": groupId, "subgroup": subGroup}).skip((int(page)-1)*8).limit(8)
    productArray = list(products)
    pageCount = math.ceil(products.count()/8)
    return render_template(
        'grid-electronics.html', 
        title='Electronics', 
        groups=groupsList, 
        products=productArray, 
        activeGroupId=groupId, 
        activeSubGroup=subGroup, 
        pageCount=pageCount,
        currentPage=page
    )

#store - gear
@app.route('/gear')
def gear1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('gear', gid=groupId, subgroup=subGroup, page=page))
@app.route('/store/gear')
def gear():
    groupId   = request.args.get("gid")
    subGroup  = request.args.get("subgroup")
    page      = request.args.get("page")
    if groupId is None:
        groupId='ALL'
    if subGroup is None:
        subGroup = 'ALL'
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    if groupId == 'ALL' and subGroup == 'ALL':
        products = db.Products.find({"category_type": "GEAR"}).skip((int(page)-1)*8).limit(8)
    else: 
        if groupId != 'ALL' and subGroup == 'ALL':
            products = db.Products.find({"category": groupId}).skip((int(page)-1)*8).limit(8)
        else:
            products = db.Products.find({"category": groupId, "subgroup": subGroup}).skip((int(page)-1)*8).limit(8)
    productArray = list(products)
    pageCount = math.ceil(products.count()/8)
    return render_template(
        'grid-gear.html', 
        title='Gear', 
        groups=groupsList, 
        products=productArray, 
        activeGroupId=groupId, 
        activeSubGroup=subGroup, 
        pageCount=pageCount,
        currentPage=page
    )

#store - computers
@app.route('/computers')
def computers1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('computers', gid=groupId, subgroup=subGroup, page=page))
@app.route('/store/computers')
def computers():
    groupId   = request.args.get("gid")
    subGroup  = request.args.get("subgroup")
    page      = request.args.get("page")
    if groupId is None:
        groupId='ALL'
    if subGroup is None:
        subGroup = 'ALL'
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    if groupId == 'ALL' and subGroup == 'ALL':
        products = db.Products.find({"category_type": "COMPUTERS"}).skip((int(page)-1)*8).limit(8)
    else: 
        if groupId != 'ALL' and subGroup == 'ALL':
            products = db.Products.find({"category": groupId}).skip((int(page)-1)*8).limit(8)
        else:
            products = db.Products.find({"category": groupId, "subgroup": subGroup}).skip((int(page)-1)*8).limit(8)
    productArray = list(products)
    pageCount = math.ceil(products.count()/8)
    return render_template(
        'grid-computers.html', 
        title='Computers', 
        groups=groupsList, 
        products=productArray, 
        activeGroupId=groupId, 
        activeSubGroup=subGroup, 
        pageCount=pageCount,
        currentPage=page
    )

#store - toys
@app.route('/toys')
def toys1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('toys', gid=groupId, subgroup=subGroup, page=page))
@app.route('/store/toys')
def toys():
    groupId   = request.args.get("gid")
    subGroup  = request.args.get("subgroup")
    page      = request.args.get("page")
    if groupId is None:
        groupId='ALL'
    if subGroup is None:
        subGroup = 'ALL'
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    if groupId == 'ALL' and subGroup == 'ALL':
        products = db.Products.find({"category_type": "TOYS"}).skip((int(page)-1)*8).limit(8)
    else: 
        if groupId != 'ALL' and subGroup == 'ALL':
            products = db.Products.find({"category": groupId}).skip((int(page)-1)*8).limit(8)
        else:
            products = db.Products.find({"category": groupId, "subgroup": subGroup}).skip((int(page)-1)*8).limit(8)
    productArray = list(products)
    pageCount = math.ceil(products.count()/8)
    return render_template(
        'grid-toys.html', 
        title='Toys', 
        groups=groupsList, 
        products=productArray, 
        activeGroupId=groupId, 
        activeSubGroup=subGroup, 
        pageCount=pageCount,
        currentPage=page
    )

#store - accessories
@app.route('/accessories')
def accessories1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('accessories', gid=groupId, subgroup=subGroup, page=page))
@app.route('/store/accessories')
def accessories():
    groupId   = request.args.get("gid")
    subGroup  = request.args.get("subgroup")
    page      = request.args.get("page")
    if groupId is None:
        groupId='ALL'
    if subGroup is None:
        subGroup = 'ALL'
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    if groupId == 'ALL' and subGroup == 'ALL':
        products = db.Products.find({"category_type": "ACCESSORIES"}).skip((int(page)-1)*8).limit(8)
    else: 
        if groupId != 'ALL' and subGroup == 'ALL':
            products = db.Products.find({"category": groupId}).skip((int(page)-1)*8).limit(8)
        else:
            products = db.Products.find({"category": groupId, "subgroup": subGroup}).skip((int(page)-1)*8).limit(8)
    productArray = list(products)
    pageCount = math.ceil(products.count()/8)
    return render_template(
        'grid-accessories.html', 
        title='Accessories', 
        groups=groupsList, 
        products=productArray, 
        activeGroupId=groupId, 
        activeSubGroup=subGroup, 
        pageCount=pageCount,
        currentPage=page
    )

#store
@app.route('/store')
def store():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('store.html', title='Store', groups=groupsList)

# shipping
@app.route('/shipping')
@login_required
def shipping():
    orders = db.Orders.find()
    c = 0
    current = {}

    while c < orders.count():
        if 'item_id' in orders[c]:
            if orders[c]['item_id'] in current:
                current[orders[c]['item_id']] += 1
            else:
                current[orders[c]['item_id']] = 1
        c += 1
    return render_template('shipping.html', breadCrumb=BREAD_CRUMB['Shipping'][0], title='Shipping', orders=current)

# Purchase
@app.route('/purchase/items')
def post_purchase():
    if request.method == 'POST':
        print("++++++++++NEW REQUEST++++++++++++")
        print(request.data)
        return redirect(url_for('post_purchase'))
    return render_template('purchase.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Purchase Order')

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
    return render_template('purchase.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Purchase Order', form=form)

# Purchase
@app.route('/bills')
@login_required
def bills():
    form = BillingForm()
    if form.validate_on_submit():
        return redirect(url_for('bills'))
    return render_template('bills.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Billing', form=form)

# groups - categorize
@app.route('/groups/category', methods=['GET','POST'])
@login_required
def groups_category():
    form = CategoryForm()
    if form.validate_on_submit():
        new_item = {
            'id' : str(uid()),
            'name' : form.name.data,
        }
        db.Category.insert_one(new_item)
        flash('New Category Added.')
        return redirect(url_for('addItem'))
    return render_template('groups-category.html', title='Groups Category', form=form)

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
            'total' : 0,
            'sub_group': request.form.getlist('subgroups')
        }
        db.Groups.insert_one(new_item)
        flash('New Group Added.')
        return redirect(url_for('groups'))
    return render_template('groups-add.html', breadCrumb=BREAD_CRUMB['Products'][0], uname=current_user.get_id(), title='Groups', form=form)

# groups
@app.route('/groups')
@login_required
def groups():
    groups = db.Groups.find()
    return render_template('groups.html', breadCrumb=BREAD_CRUMB['Products'][0], uname=current_user.get_id(), title='Groups', groups=groups)

# groups list
@app.route('/groups/<name>', methods=['GET','POST'])
@login_required
def groups_list(name):
    if request.method == 'POST':
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
        print(update_item)

        db.Products.update_one({"id": request.form.get("pid")},{"$set":update_item},upsert=True)

    try:
        group = db.Groups.find({'name':str(name)})
        items = db.Products.find({'category':group[0]['id']})
        if items.count() == 0:
            flash("Product Does Not Exist")
            return redirect(url_for('addItem'))

        cates = getGroups()
        product_id = items[0]['id']

        #bug - temp solution
        vendors = {'none':'None'}

        ordrs = db.Orders.find({'item_id':product_id})
        #ordrs = db.Orders.find()

        hists = db.History.find({'pid':product_id})

        #print( items.__dict__ )        print(items[0])
    except TypeError:
        flash("Group Does Not Exist")
        return redirect(url_for('groups'))
    if request.method == 'GET':
        CURRENCIES=[('USD', '$'),('EURO','€'),('POUND', '£')]
        
    return render_template('groups-list.html', breadCrumb=BREAD_CRUMB['Products'][0],
                            uname=current_user.get_id(), title='Groups List', items=items, cates=cates,
                            vendors=vendors, currs=CURRENCIES, orders=ordrs, history=hists)

@app.route('/getSubgroups', methods=['POST'])
@login_required
def getSubgroups():
    if request.method == 'POST':
        item = request.json
        if not item: return jsonify(subgroups=[('none', 'None')])
        
        print("++++++++++NEW REQUEST++++++++++++ getSubgroups: ", item)
        group = db.Groups.find_one({'id':item['id']})
        if not 'sub_group' in group:
            group['sub_group'] = [('none', 'None')]
        return jsonify(subgroups=group['sub_group'])

@app.route('/updateProduct', methods=['POST'])
@login_required
def updateProduct():
    if request.method == 'POST':
        update_item = request.json
        db.Products.update_one({"id": update_item['pid']},{"$set":update_item['item']},upsert=True)

        return jsonify(result="success")

@app.route('/getProduct', methods=['POST'])
@login_required
def getProduct():
    if request.method == 'POST':
        item = request.json
        print("++++++++++NEW REQUEST++++++++++++ getProduct: ", item)
        prdt = db.Products.find_one({'id':item['pid']})

        return jsonify(id=prdt['id'], product=prdt['product'], sku=prdt['sku'], #'images' : prdt['images'],
                        category=prdt['category'], price=prdt['price'], currency=prdt['currency'],
                        attributes=prdt['attributes'], vendor=prdt['vendor'], url=prdt['url'])

# get orders
@app.route('/getOrders', methods=['POST'])
@login_required
def getOrders():
    if request.method == 'POST':
        item = request.json
        ordrs = db.Orders.find({'item_id':item['pid']})

        arrOrder = []
        for order in ordrs:
            arrOrder.append({"oid":order['order_id'], "playerid":order['player_id'],
            "itemid":order['item_id'], "qty":order['quantity'], "type":order['type'],
            "price":order['price']})

        return jsonify(orders=arrOrder)

# get history
@app.route('/getHistory', methods=['POST'])
@login_required
def getHistory():
    if request.method == 'POST':
        item = request.json
        print("++++++++++ getHistory ++++++++++++ item: ", item)
        hists = db.History.find({'pid':item['pid']})
        arrHist = []
        for hist in hists:
            arrHist.append({"type":hist['type'], "date":hist['date'], "reason":hist['reason'],
            "adjustments":hist['adjustments'], "description":hist['description']})

        return jsonify(history=arrHist)

# add history
@app.route('/addHistory', methods=['POST'])
@login_required
def addHistory():
    if request.method == 'POST':
        item = request.json
        arrHist = []

        for hist in item['chgs']:
            hist = hist.split(',')
            new_item = {
                'id' : str(uid()),
                'pid' : hist[2],
                'type' : hist[0],
                'date' : hist[1],
                'reason' : "Item Updated",
                'adjustments' : hist[2],
                'description' : "User ID: "+current_user.get_id(),
            }

            db.History.insert_one(new_item)
            arrHist.append({'id' : str(uid()),'pid' : hist[2],'type' : hist[0],
                'date' : hist[1],'reason' : "Item Updated",'adjustments' : hist[2],
                'description' : "User ID: "+current_user.get_id() } )

        return jsonify(history=arrHist)

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
    return render_template('vendor.html', breadCrumb=BREAD_CRUMB['Products'][0],
    uname=current_user.get_id(), title='Vendor', form=form)

@app.route('/uploadLogo', methods=['POST'])
@login_required
def uploadLogo():
    curDirPath = os.path.dirname(os.path.realpath(__file__))
    UPLOAD_FOLDER = os.path.join(curDirPath,"uploads/logo")
    file_urls = []
    if(request.method == 'POST') and 'file' in request.files:
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
                file_urls.append('../uploads/logo/' + filename)
        strjson = file_urls[0]
        return jsonify(target_file=strjson)
    return ''
# products - add item
@app.route('/products/add', methods=['GET','POST'])
@login_required
def addItem():
    curDirPath = os.path.dirname(os.path.realpath(__file__))
    UPLOAD_FOLDER = os.path.join(curDirPath,"uploads")
    form = ProductForm()
    form.update_category()
    file_urls = []
    print("\n routes : addItem > $$$$$$$$$$$$$$$$$$")
    if(request.method == 'POST') and 'photos' in request.files:
        #print(request.files)
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
                file_urls.append('../uploads/' + filename)
        strjson = file_urls[0]
        print("------strjson: "+strjson)
        return jsonify(target_file=strjson)
        
    if form.validate_on_submit():
        # add new vendor
        vendor = ""
        if form.vendor.data != "none":
            vendor = form.vendor.data

        # add new product
        attrs = {form.attr0.data:form.options0.data}
        if form.attr1.data != "":
            attrs[form.attr1.data] = form.options1.data
        if form.attr2.data != "":
            attrs[form.attr2.data] = form.options2.data
        images = form.hdfiles.data
        #images = images.split(",")
        print("\n routes | addItem: ----------------------------")
        
        category_type = db.Groups.find_one({"id": form.category.data})["type"]
        new_item = {
            'id' : str(uid()),
            'product' : form.product.data,
            'sku' : form.sku.data,
            'images' : images,
            'category_type': category_type,
            'category' : form.category.data,
            'subgroup' : form.subgroup.data,
            'price' : form.price.data,
            'currency' : form.currency.data,
            'attributes' : attrs,
            'vendor' : vendor,
            'url' : form.url.data,
        }
        db.Products.insert_one(new_item)

        #Add History
        new_hist_item = {
            'id' : str(uid()),
            'pid' : new_item['id'],
            'type' : 'ITEM',
            'date' : date.today().strftime('%Y/%m/%d'),
            'reason' : "New Item Created",
            'adjustments' : new_item['id'],
            'description' : "User ID: "+current_user.get_id(),
        }
        db.History.insert_one(new_hist_item)

        # update Groups inventory count
        current = db.Groups.find_one({'id': form.category.data})
        db.Groups.update_one(current,{"$set":{'total': current['total']+1}})

        flash('New Item Added.')
        return redirect(url_for('products'))

    return render_template('add-item.html', breadCrumb=BREAD_CRUMB['Products'][0], uname=current_user.get_id(), title='Add Item', form=form)

@app.route('/importFile', methods=['GET','POST'])
@login_required
def importItem():
    if request.method == 'POST':
        ### Save uploaded file
        f = request.files['fileImport']
        #data_xls = pd.read_excel(f, sheet_name='Sheet1'); for i in data_xls.index:print(data_xls['Product Name'][i])
        #data_csv = pd.read_csv(f, low_memory=False); print(list(data_csv))
        filename = secure_filename(f.filename)
        impfilepath = os.path.join(UPLOAD_FOLDER, filename)
        f.save(impfilepath)

        ### Read and Save into DB
        with open(impfilepath, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:                
                if line_count == 0:
                    print(f'-----> Column names are {", ".join([str(i) for i in row])}')
                    #line_count += 1; continue
                print(json.dumps(row,indent=4)) #print(f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.')
                #line_count += 1; continue
                ## 0-Product Name, 1-SKU, 2-Category, 3-Price, 4-Currency, 5-Attributes, 6-Vendor, 7-URL
                new_item = {
                    'id' : str(uid()),
                    'product' : row['Product Name'],
                    'sku' : row['SKU'],
                    #'images' : images,
                    'category' : row['Category'],
                    'price' : row['Price'],
                    'currency' : row['Currency'],
                    'attributes' : json.loads(row['Attributes'].replace('/',',')),
                    'vendor' : row['Vendor'],
                    'url' : row['URL'],
                }
                db.Products.insert_one(new_item)

                ###Add History
                new_hist_item = {
                    'id' : str(uid()),
                    'pid' : new_item['id'],
                    'type' : 'ITEM',
                    'date' : date.today().strftime('%Y/%m/%d'),
                    'reason' : "New Item Created",
                    'adjustments' : new_item['id'],
                    'description' : "User ID: "+current_user.get_id(),
                }
                db.History.insert_one(new_hist_item)

                ###Update Groups inventory count
                current = db.Groups.find_one({'id': new_item['category']})
                db.Groups.update_one(current,{"$set":{'total': current['total']+1}})

                line_count += 1

            print(f'Processed {line_count} lines.')        

        return 'file uploaded successfully'

# products
@app.route('/products', methods=['GET','POST'])
@login_required
def products():
    if request.method == 'POST':
        item = request.json
        #order = db.Orders.find_one({'order_id':item['id']})
        #post_cancellation_request(order['merchant_order_id'])
        
        db.Products.remove({'id':item['id']})

        #Add History
        new_hist_item = {
            'id' : str(uid()),
            'pid' : item['id'],
            'type' : 'ITEM',
            'date' : date.today().strftime('%Y/%m/%d'),
            'reason' : "Item Deleted",
            'adjustments' : item['id'],
            'description' : "User ID: "+current_user.get_id(),
        }
        db.History.insert_one(new_hist_item)

        response = app.response_class(
            response=json.dumps(item),
            status=200,
            mimetype='application/json'
        )
        return response

    tblPrdt = []
    table = db.Products.find()
    for prdt in table:
        cid = prdt['category']
        cname = ""
        grp = db.Groups.find_one({'id':cid})
        if grp:
            cname = grp['name']
        
        vid = prdt['vendor']
        vname = ""
        vdr = db.Vendor.find_one({'id':vid})
        if vdr:            
            vname = vdr['vendor']
        #print("--- prdt: ",prdt,", cid: ",cid,", cname: ",cname,", vname: ",vname)

        qty = "-"
        if 'quantity' in prdt:
            qty = prdt['quantity']

        tblPrdt.append({ #Variable 'table' is just iterator, so it indicates the NULL after finished loop
            'id': prdt['id'],
            'product': prdt['product'],
            'category': cname,
            'price': prdt['price'],
            'currency': prdt['currency'],
            'quantity': qty,
            'vendor': vname,
        })
    '''
    for prdt in table:
        print("--- prdt: ",prdt)
    '''

    return render_template('products.html', breadCrumb=BREAD_CRUMB['Products'][0], uname=current_user.get_id(), title='Products', table=tblPrdt)

# inventory - product orders
@app.route('/reports/activity-mail')
@login_required
def activity_mail():
    return render_template('activity-mail.html', breadCrumb=BREAD_CRUMB['Reports'][0], uname=current_user.get_id(), title='Activity Mail')

# inventory - product orders
@app.route('/reports/activity-log')
@login_required
def activity_log():
    return render_template('activity-log.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Activity Log')

# inventory - product orders
@app.route('/reports/purchases-orders', methods=['GET','POST'])
@login_required
def purchases_orders():
    if request.method == 'POST':
        result = db.Orders.find({
            "date": {
                "$gt": date.strptime(request.json["from"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                "$lte": date.strptime(request.json["to"], "%Y-%m-%dT%H:%M:%S.%fZ")
            },
        }, {
            "_id": 0
        })
        return jsonify({"report": list(result)})
    return render_template('purchases-orders.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases Orders')

# inventory - product receivable
@app.route('/reports/purchases-receivable', methods=['GET','POST'])
@login_required
def purchases_receivable():
    if request.method == 'POST':
        if request.json["receivable"] == 'Receivable':
            result = db.Orders.find({
                "invoice_id": {"$ne": None}
            }, {
                "_id": 0
            })
        else:
            result = db.Orders.find({
                "invoice_id": None
            }, {
                "_id": 0
            })
        return jsonify({"report": list(result)})
    
    return render_template('purchases-receivable.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases Details')

# inventory - product sales
@app.route('/reports/purchases-vendors', methods=['GET','POST'])
@login_required
def purchases_vendors():
    if request.method == 'POST':
        products = db.Products.find({
            "vendor": request.json["vendor"]
        })
        productIdArray = []
        for product in products:
            productIdArray.append(product["id"])
        
        result = db.Orders.find({
            "product_id": {
                "$in": productIdArray
            }
        }, {
            "_id": 0
        })
        return jsonify({"report": list(result)})
    vendors = db.Vendor.find()
    return render_template('purchases-vendors.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases By Vendors', vendors=vendors)

# inventory - product sales
@app.route('/reports/purchases-items', methods=['GET','POST'])
@login_required
def purchases_items():
    if request.method == 'POST':
        result = db.Orders.find({
            "product_id": request.json["product_id"]
        }, {
            "_id": 0
        })
        return jsonify({"report": list(result)})
    products = db.Products.find()
    return render_template('purchases-items.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases by Items', products=products)
# inventory - purchase bills
@app.route('/reports/purchases-bills')
@login_required
def purchases_bills():
    return render_template('purchases-bills.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases by Bills')

# inventory - purchase balance
@app.route('/reports/purchases-balance')
@login_required
def purchases_balance():
    return render_template('purchases-balance.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Vendor Balance')

# inventory - product sales
@app.route('/reports/purchases-payments')
@login_required
def purchases_payments():
    return render_template('purchases-payments.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases by Payments')

# inventory - product sales
@app.route('/reports/inventory-fifo')
@login_required
def inventory_fifo():
    return render_template('inventory-fifo.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='FIFO')

# inventory - product sales
@app.route('/reports/inventory-valuation')
@login_required
def inventory_valuation():
    return render_template('inventory-valuation.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Inventory Valuation')

# inventory - product sales
@app.route('/reports/inventory-details')
@login_required
def inventory_details():
    return render_template('inventory-details.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Inventory Details')

# inventory - product sales
@app.route('/reports/inventory-sales')
@login_required
def inventory_sales():
    return render_template('inventory-sales.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Product Sales')

# inventory - order history
@app.route('/reports/inventory-purchases')
@login_required
def inventory_purchases():
    return render_template('inventory-purchases.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Active Purchases')

# sales -
@app.route('/reports/sales-item')
@login_required
def sales_item():
    return render_template('sales-item.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Items')

# inventory - product sales
@app.route('/reports/salesman')
@login_required
def salesman():
    return render_template('salesman.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Salesman')

# inventory - product sales
@app.route('/reports/sales-balance')
@login_required
def sales_balance():
    return render_template('sales-balance.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Balance')

# sales - packing history
@app.route('/reports/sales-packing')
@login_required
def sales_packing():
    return render_template('sales-packing.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Packing')

# sales - payment history
@app.route('/reports/sales-payments')
@login_required
def sales_payments():
    return render_template('sales-payments.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Payments')

# sales - invoice history
@app.route('/reports/sales-customers')
@login_required
def sales_customers():
    return render_template('sales-customers.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Customer')

# sales - sales orders
@app.route('/reports/sales-orders')
@login_required
def sales_orders():
    return render_template('sales-orders.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Order')

# sales - sales product
@app.route('/reports/sales-invoice')
@login_required
def sales_invoice():
    return render_template('sales-invoice.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Invoices')

# integrations
@app.route('/integrations')
@login_required
def integrations():
    print("----------------------------- bread_crumb:", bread_crumb['Integrations'])
    return render_template('integrations.html', breadCrumb=BREAD_CRUMB['Integrations'][0],
    uname=current_user.get_id(), title='Integrations')

# reports
@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Report')

# billing
@app.route('/billing')
@login_required
def billing():
    return render_template('billing.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Billing')

# checkout
@app.route('/checkout', methods=['GET','POST'])
@login_required
def checkout():
    if request.method == 'GET':
        ordersByProduct = db.Orders.aggregate([
            { "$match": { "invoice_id": None } },
            {
                "$group": 
                {
                    "_id": { 
                        "product_id": "$product_id",
                        "product_name": "$product_name"
                    },
                    "price": {
                        "$sum": { 
                            "$multiply": [ "$price", "$quantity" ]
                        } 
                    },
                    "quantity": { 
                        "$sum": "$quantity"
                    },
                    "count": { "$sum": 1 },
                }
            },
            { "$sort": { "_id": 1} }
        ])
        total = db.Orders.aggregate([
            { "$match": { "invoice_id": None } },
            {
                "$group": {
                    "_id": None,
                    "price": {
                        "$sum": {
                            "$multiply": [ "$price", "$quantity" ]
                        }
                    },
                    "count": { "$sum": 1 },
                }
            }
        ])
        ordersByProductList = list(ordersByProduct)
        return render_template('checkout.html', title='Checkout', ordersByProduct=ordersByProductList, total=(list(total))[0])
    
    ######################################
    ### Adding Cart
    ######################################
    cartData = request.form.get('cart-data')
    # when carts is empty
    if cartData == '': 
        return render_template('checkout.html', title='Checkout', ordersByProduct=[], total={"count": 0, "price": 0})    
    
    # when carts has some products
    cartStrArray = cartData.split(';')
    ordersByProduct = []
    total = {"count": 0, "price": 0}
    for x in cartStrArray:
        y = x.split(',')
        product = db.Products.find_one({"id": y[0]})
        ordersByProduct.append({
            "_id": { 
                "product_id": product['id'],
                "product_name": product['product']
            },
            "price": product['price'],
            "count": int(y[1]),
            "quantity": int(y[1])
        })
        total["count"] += int(y[1])
        total["price"] += int(y[1])*product['price']
        db.Orders.insert_one({
            'order_id': str(uid()),
            'player_id': str(uid()),
            'product_id': product['id'],
            'product_name': product['product'],
            'group_id': product['category'],
            'subgroup': product['subgroup'],
            'quantity': int(y[1]),
            'type': 'store',
            'price': product['price'],
            'street': _street(),
            'city' : _getCity(),
            'state' : _getState(),
            'zip' : _getZip(),
            'country': 'US',
            'ship_id': None,
            'invoice_id': None,
            'date': datetime.now()
        })
    return render_template('checkout.html', title='Checkout', ordersByProduct=ordersByProduct, total=total)
# exports
@app.route('/files')
@login_required
def files():
    return render_template('files.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Files')

# contacts
@app.route('/contacts')
@login_required
def contacts():
    return render_template('contacts.html', breadCrumb=BREAD_CRUMB['Shipping'][0],
    uname=current_user.get_id(), title='Contacts')

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

    tblOrdrs = []
    table = db.Orders.find()
    for ordr in table:
        uid = ordr['player_id']
        pname = ""
        plyr = db.Users.find_one({'uid':uid})
        if plyr:
            pname = plyr['name']
        
        iname = ""
        if 'item_id' in ordr:
            iid = ordr['item_id']            
            itm = db.Products.find_one({'id':iid})
            if itm:            
                iname = itm['product']
        #print("--- prdt: ",prdt,", cid: ",cid,", cname: ",cname,", vname: ",vname)

        tblOrdrs.append({ #Variable 'table' is just iterator, so it indicates the NULL after finished loop
            'order_id': ordr['order_id'],
            'player': pname,
            'item': iname,
            'quantity': ordr['quantity'],
            'type': ordr['type'],
            'price': ordr['price']
        })

    return render_template('orders.html', breadCrumb=BREAD_CRUMB['Orders'][0], uname=current_user.get_id(), title='Queue', table=tblOrdrs)

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
    return render_template('queue.html', breadCrumb=BREAD_CRUMB['Queue'][0],
    uname=current_user.get_id(), title='Queue', queue=queue, qlen=queue.count())

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
    return render_template('signup.html', breadCrumb=BREAD_CRUMB['Signup'][0], title='Register', form=form)

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
    return render_template('login.html', breadCrumb=BREAD_CRUMB['Login'][0], title='Login', form=form)

# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/uploads/<path:path>')
def send_images(path):
    return send_from_directory('uploads', path)
