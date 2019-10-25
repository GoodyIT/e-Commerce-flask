from app import db
from flask import render_template, json, url_for, flash, redirect, request, \
jsonify, g, Flask, send_from_directory, get_flashed_messages
from flask_login import login_user, logout_user, login_required, current_user
from uuid import uuid4 as uid
from datetime import datetime as date
from werkzeug.utils import secure_filename
from .forms import RegisterForm, LoginForm, ProductForm, PurchaseForm, GroupForm, \
VendorForm, BillingForm, StoreLoginForm, StoreSignupForm, UpdatePaymentsForm, \
EmailForm, TextForm, SettingsForm, CouponForm
from .data import User
from datetime import datetime
from . import *

import json, os, math, random, pandas, csv, pdb

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
'Orders':['Orders','orders'], 'Shipping':['Shipping','Contacts'], 'Profile': ['Profile']}

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

# Error handling
@admin_bp.errorhandler(404)
def not_found_error(error):
    return render_template('admin/404.html'), 404

# Internal handling
@admin_bp.errorhandler(500)
def internal_error(error):
    return render_template('admin/500.html'), 500

# home page
@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def home():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    products = db.Products.find()
    return render_template(
        'admin/index.html',
        breadCrumb=BREAD_CRUMB['Dashboard'][0],
        uname=current_user.get_id(),
        avatar=current.get('avatar'),
        title='Home Page',
        total=products
        )

# Get analytics
@admin_bp.route('/analytics', methods=['GET', 'POST'])
@login_required
def get_analytics():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    requestData = json.loads(request.data.decode('utf-8'))
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
        import pdb; pdb.set_trace()
        return jsonify({
            "analyticsByYearly"   : list(analyticsByYearly),
            "analyticsByState"    : list(analyticsByState),
            "analyticsByGroup"    : analyticsByGroupArray,
            "totalCost"           : totalQuantityAndCostArray[0]['price'] if totalQuantityAndCostArray else '',
            "totalQuantity"       : totalQuantityAndCostArray[0]['quantity'] if totalQuantityAndCostArray else '',
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

@admin_bp.route('/product_detail/<string:item>', methods=['GET', 'POST'])
def product_detail(item):
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    product = db.Products.find_one({"id": item})
    vendor = db.Vendors.find_one({"id": product.get("vendor")})
    category = db.Groups.find_one({"id": product.get("category")})
    return render_template(
        'admin/product_detail.html',
        title='Product Detail',
        groups=groupsList,
        product=product
        # activeGroupId=groupId,
        # activeSubGroup=subGroup,
        # pageCount=pageCount,
        # currentPage=page,
        # is_authenticated=current_user.is_authenticated
    )

#store - games
@admin_bp.route('/games', methods=['GET', 'POST'])
def games1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('admin.games', gid=groupId, subgroup=subGroup, page=page))

@admin_bp.route('/store/games', methods=['GET', 'POST'])
def games():
    groupId   = request.args.get("gid")
    subGroup  = request.args.get("subgroup")
    page      = request.args.get("page")
    sortBy    = request.args.get("sort")
    accending = request.args.get("accending")
    mode = request.args.get('mode')
    if request.args.get("accending") == None:
        accending = "-1"
    if request.args.get("sort") == None:
        sortBy = "date"
    if groupId is None:
        groupId='ALL'
    if subGroup is None:
        subGroup = 'ALL'
    if mode is None:
        mode = 'relevance'
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    if groupId == 'ALL' and subGroup == 'ALL':
        products = db.Products.find({"category_type": "GAMES"}).sort(sortBy,int(accending,10)).skip((int(page)-1)*8).limit(8)
    else:
        if groupId != 'ALL' and subGroup == 'ALL':
            products = db.Products.find({"category": groupId}).sort(sortBy,int(accending,10)).skip((int(page)-1)*8).limit(8)
        else:
            products = db.Products.find({"category": groupId, "subgroup": subGroup}).sort(sortBy,int(accending,10)).skip((int(page)-1)*8).limit(8)
    productArray = list(products)
    pageCount = math.ceil(products.count()/8)
    return render_template(
        'admin/grid-games.html',
        title='Games',
        groups=groupsList,
        products=productArray,
        activeGroupId=groupId,
        activeSubGroup=subGroup,
        pageCount=pageCount,
        currentPage=page,
        accending=accending,
        mode=mode,
        is_authenticated=current_user.is_authenticated
    )

#store - office
@admin_bp.route('/office', methods=['GET', 'POST'])
def office1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('admin.office', gid=groupId, subgroup=subGroup, page=page))

@admin_bp.route('/store/office', methods=['GET', 'POST'])
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
        'admin/grid-office.html',
        title='Office',
        groups=groupsList,
        products=productArray,
        activeGroupId=groupId,
        activeSubGroup=subGroup,
        pageCount=pageCount,
        currentPage=page,
        is_authenticated=current_user.is_authenticated
    )

#store - electronics
@admin_bp.route('/electronics', methods=['GET', 'POST'])
def electrnoics1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('admin.electronics', gid=groupId, subgroup=subGroup, page=page))

@admin_bp.route('/store/electronics', methods=['GET', 'POST'])
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
        'admin/grid-electronics.html',
        title='Electronics',
        groups=groupsList,
        products=productArray,
        activeGroupId=groupId,
        activeSubGroup=subGroup,
        pageCount=pageCount,
        currentPage=page,
        is_authenticated=current_user.is_authenticated
    )

#store - gear
@admin_bp.route('/gear', methods=['GET', 'POST'])
def gear1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('admin.gear', gid=groupId, subgroup=subGroup, page=page))

@admin_bp.route('/store/gear', methods=['GET', 'POST'])
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
        'admin/grid-gear.html',
        title='Gear',
        groups=groupsList,
        products=productArray,
        activeGroupId=groupId,
        activeSubGroup=subGroup,
        pageCount=pageCount,
        currentPage=page,
        is_authenticated=current_user.is_authenticated
    )

#store - computers
@admin_bp.route('/computers', methods=['GET', 'POST'])
def computers1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('admin.computers', gid=groupId, subgroup=subGroup, page=page))

@admin_bp.route('/store/computers', methods=['GET', 'POST'])
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
        'admin/grid-computers.html',
        title='Computers',
        groups=groupsList,
        products=productArray,
        activeGroupId=groupId,
        activeSubGroup=subGroup,
        pageCount=pageCount,
        currentPage=page,
        is_authenticated=current_user.is_authenticated
    )

#store - toys
@admin_bp.route('/toys', methods=['GET', 'POST'])
def toys1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('admin.toys', gid=groupId, subgroup=subGroup, page=page))

@admin_bp.route('/store/toys', methods=['GET', 'POST'])
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
        'admin/grid-toys.html',
        title='Toys',
        groups=groupsList,
        products=productArray,
        activeGroupId=groupId,
        activeSubGroup=subGroup,
        pageCount=pageCount,
        currentPage=page,
        is_authenticated=current_user.is_authenticated
    )

#store - accessories
@admin_bp.route('/accessories', methods=['GET', 'POST'])
def accessories1():
    groupId = request.args.get("gid")
    subGroup = request.args.get("subgroup")
    page     = request.args.get("page")
    return redirect(url_for('admin.accessories', gid=groupId, subgroup=subGroup, page=page))

@admin_bp.route('/store/accessories', methods=['GET', 'POST'])
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
        'admin/grid-accessories.html',
        title='Accessories',
        groups=groupsList,
        products=productArray,
        activeGroupId=groupId,
        activeSubGroup=subGroup,
        pageCount=pageCount,
        currentPage=page,
        is_authenticated=current_user.is_authenticated
    )

#store
@admin_bp.route('/', methods=['GET', 'POST'])
def store():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/store.html', title='Store', groups=groupsList, is_authenticated=current_user.is_authenticated)

# shipping
@admin_bp.route('/shipping', methods=['GET', 'POST'])
@login_required
def shipping():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    orders = db.Orders.find({"status": "Await shipping"}, {"_id": 0})
    c = 0
    currents = {}

    # while c < orders.count():
    #     if 'product_id' in orders[c]:
    #         if orders[c]['product_id'] in currents:
    #             currents[orders[c]['product_id']] += 1
    #         else:
    #             currents[orders[c]['product_id']] = 1
    #     c += 1
    return render_template('admin/shipping.html', breadCrumb=BREAD_CRUMB['Shipping'][0], title='Shipping', orders=orders
        ,avatar=current.get('avatar'))

# Purchase
@admin_bp.route('/purchase/items', methods=['GET', 'POST'])
def post_purchase():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        print("++++++++++NEW REQUEST++++++++++++")
        print(request.data)
        return redirect(url_for('admin.post_purchase'))
    return render_template('admin/purchase.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Purchase Order',avatar=current.get('avatar'))

# Purchase
@admin_bp.route('/purchase', methods=['GET', 'POST'])
@login_required
def purchase():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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

        return redirect(url_for('admin.purchase'))
    return render_template('admin/purchase.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Purchase Order', form=form,avatar=current.get('avatar'))

# Purchase
@admin_bp.route('/bills', methods=['GET', 'POST'])
@login_required
def bills():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    form = BillingForm()
    if form.validate_on_submit():
        return redirect(url_for('admin.bills'))
    return render_template('admin/bills.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Billing', form=form,avatar=current.get('avatar'))

# groups - categorize
@admin_bp.route('/groups/category', methods=['GET', 'POST'])
@login_required
def groups_category():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    form = CategoryForm()
    if form.validate_on_submit():
        new_item = {
            'id' : str(uid()),
            'name' : form.name.data,
        }
        db.Category.insert_one(new_item)
        flash('New Category Added.')
        return redirect(url_for('admin.addItem'))
    return render_template('admin/groups-category.html', title='Groups Category', form=form,avatar=current.get('avatar'))

# groups add
@admin_bp.route('/groups/add', methods=['GET', 'POST'])
@login_required
def groups_add():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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
        return redirect(url_for('admin.groups'))
    return render_template('admin/groups-add.html', breadCrumb=BREAD_CRUMB['Products'][0], uname=current_user.get_id(), title='Groups', form=form,avatar=current.get('avatar'))

# groups
@admin_bp.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    groups = db.Groups.find()
    return render_template('admin/groups.html', breadCrumb=BREAD_CRUMB['Products'][0], uname=current_user.get_id(), title='Groups', groups=groups,avatar=current.get('avatar'))

# groups list
@admin_bp.route('/groups/<name>', methods=['GET', 'POST'])
@login_required
def groups_list(name):
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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
            return redirect(url_for('admin.addItem'))

        cates = getGroups()
        product_id = items[0]['id']

        vendorData = db.Vendor.find({})
        vendors = {}
        for vendor in vendorData:
            vendors[vendor['id']] = vendor["vendor"]

        ordrs = db.Orders.find({'item_id':product_id})
        #ordrs = db.Orders.find()

        hists = db.History.find({'pid':product_id})

        #print( items.__dict__ )        print(items[0])
    except TypeError:
        flash("Group Does Not Exist")
        return redirect(url_for('admin.groups'))
    if request.method == 'GET':
        CURRENCIES=[('USD', '$'),('EURO','€'),('POUND', '£')]
    print("----")
    print(vendors)
    return render_template('admin/groups-list.html', breadCrumb=BREAD_CRUMB['Products'][0],
                            uname=current_user.get_id(), title='Groups List', items=items, cates=cates,
                            vendors=vendors, currs=CURRENCIES, orders=ordrs, history=hists,avatar=current.get('avatar'))

@admin_bp.route('/getSubgroups', methods=['GET', 'POST'])
@login_required
def getSubgroups():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        item = request.json
        if not item: return jsonify(subgroups=[('none', 'None')])

        print("++++++++++NEW REQUEST++++++++++++ getSubgroups: ", item)
        group = db.Groups.find_one({'id':item['id']})
        if not 'sub_group' in group:
            group['sub_group'] = [('none', 'None')]
        return jsonify(subgroups=group['sub_group'])

@admin_bp.route('/updateProuct', methods=['GET', 'POST'])
@login_required
def updateProduct():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        update_item = request.json
        db.Products.update_one({"id": update_item['pid']},{"$set":update_item['item']},upsert=True)

        return jsonify(result="success")

@admin_bp.route('/getProduct', methods=['GET', 'POST'])
@login_required
def getProduct():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        item = request.json
        print("++++++++++NEW REQUEST++++++++++++ getProduct: ", item)
        prdt = db.Products.find_one({'id':item['pid']})

        return jsonify(id=prdt['id'], product=prdt['product'], sku=prdt['sku'], #'images' : prdt['images'],
                        category=prdt['category'], price=prdt['price'], currency=prdt['currency'],
                        attributes=prdt['attributes'], vendor=prdt['vendor'], url=prdt['url'],avatar=current.get('avatar'))

# get orders
@admin_bp.route('/getOrders', methods=['GET', 'POST'])
@login_required
def getOrders():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        item = request.json
        ordrs = db.Orders.find({'product_id':item['pid']})

        arrOrder = []
        for order in ordrs:
            arrOrder.append({"oid":order['order_id'], "playerid":order['player_id'],
            "itemid":order['product_id'], "qty":order['quantity'], "type":order['type'],
            "price":order['price']})

        return jsonify(orders=arrOrder)

# get history
@admin_bp.route('/getHistory', methods=['GET', 'POST'])
@login_required
def getHistory():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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
@admin_bp.route('/addHistory', methods=['GET', 'POST'])
@login_required
def addHistory():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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
@admin_bp.route('/products/vendor', methods=['GET', 'POST'])
@login_required
def vendor():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    vendors = db.Vendor.find({},{"_id": 0})
    form = VendorForm()
    if form.validate_on_submit():
        vendor = {
            'id' : str(uid()),
            'vendor' : form.vendor.data,
            'url' : form.url.data
        }
        db.Vendor.insert_one(vendor)
        flash('New Vendor Added.')
        return redirect(url_for('admin.vendor'))
    return render_template('admin/vendor.html', breadCrumb=BREAD_CRUMB['Products'][0],
    uname=current_user.get_id(), title='Vendor', form=form, vendors=vendors, avatar=current.get('avatar'))

@admin_bp.route('/uploadLogo', methods=['GET', 'POST'])
@login_required
def uploadLogo():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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
                file_urls.append('../uploads/logo' + filename)
        strjson = file_urls[0]
        return jsonify(target_file=strjson)
    return ''

# products - add item
@admin_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def addItem():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    # curDirPath = os.path.dirname(os.path.realpath(__file__))
    UPLOAD_FOLDER = os.path.join("app/static","uploads")
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
            'date' : datetime.now()
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
        return redirect(url_for('admin.products'))

    return render_template('admin/add-item.html', breadCrumb=BREAD_CRUMB['Products'][0], uname=current_user.get_id(), title='Add Item', form=form,avatar=current.get('avatar'))

@admin_bp.route('/importFile', methods=['GET', 'POST'])
@login_required
def importItem():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        ### Save uploaded file
        f = request.files['fileImport']
        #data_xls = pd.read_excel(f, sheet_name='Sheet1'); for i in data_xls.index:print(data_xls['Product Name'][i])
        #data_csv = pd.read_csv(f, low_memory=False); print(list(data_csv))
        filename = secure_filename(f.filename)
        impfilepath = os.path.join('app/static/uploads', filename)
        f.save(impfilepath)

        ### Read and Save into DB
        with open(impfilepath, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                # if line_count == 0:
                #     print(f'-----> Column names are {", ".join([str(i) for i in row])}')
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
                    'attributes' : json.loads(row['Attributes'].replace('',',')),
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

            # print(f'Processed {line_count} lines.')

        return 'file uploaded successfully'

# products
@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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

    return render_template('admin/products.html', breadCrumb=BREAD_CRUMB['Products'][0], uname=current_user.get_id(), title='Products', table=tblPrdt,avatar=current.get('avatar'))

@admin_bp.route('/products/delete/<string:item>', methods=['GET', 'POST'])
def delete_product(item):
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    pro = db.Products.find_one({'id': item})

    groupdata = db.Groups.find_one({'id': pro['category']})
    db.Groups.update_one(groupdata,{"$set":{'total': groupdata['total']-1}})
    db.Products.remove({'id':item})
    #Add History
    new_hist_item = {
        'id' : str(uid()),
        'pid' : item,
        'type' : 'ITEM',
        'date' : date.today().strftime('%Y/%m/%d'),
        'reason' : "Item Deleted",
        'adjustments' : item,
        'description' : "User ID: "+current_user.get_id(),
    }
    db.History.insert_one(new_hist_item)
    return redirect(url_for('admin.products'))

@admin_bp.route('/products/vendor/delete/<string:item>', methods=['GET', 'POST'])
def delete_vendor(item):
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})


    db.Vendor.remove({'id':item})
    products = db.Products.find({'vendor':item})

    for pro in products:
        groupdata = db.Groups.find_one({'id': pro['category']})
        db.Groups.update_one(groupdata,{"$set":{'total': groupdata['total']-1}})
        db.Products.remove({'id':pro['id']})

    #Add History
    new_hist_item = {
        'id' : str(uid()),
        'pid' : item,
        'type' : 'Vendor',
        'date' : date.today().strftime('%Y/%m/%d'),
        'reason' : "Vendor Deleted",
        'adjustments' : item,
        'description' : "User ID: "+current_user.get_id(),
    }
    db.History.insert_one(new_hist_item)
    return redirect(url_for('admin.vendor'))

# inventory - product orders
@admin_bp.route('/reports/activity-mail', methods=['GET', 'POST'])
@login_required
def activity_mail():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/activity-mail.html', breadCrumb=BREAD_CRUMB['Reports'][0], uname=current_user.get_id(), title='Activity Mail',avatar=current.get('avatar'))

# inventory - activity-log
@admin_bp.route('/reports/activity-log', methods=['GET', 'POST'])
@login_required
def activity_log():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.History.find({
            "date": {
                "$gt": request.json["from"],
                "$lte": request.json["to"]
            },
        }, {
            "_id": 0
        })
        return jsonify({"report": list(result)})
    return render_template('admin/activity-log.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Activity Log',avatar=current.get('avatar'))

# inventory - product orders
@admin_bp.route('/reports/purchases-orders', methods=['GET', 'POST'])
@login_required
def purchases_orders():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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
    return render_template('admin/purchases-orders.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases Orders',avatar=current.get('avatar'))

# inventory - product receivable
@admin_bp.route('/reports/purchases-receivable', methods=['GET', 'POST'])
@login_required
def purchases_receivable():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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

    return render_template('admin/purchases-receivable.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases Details',avatar=current.get('avatar'))

# inventory - product sales
@admin_bp.route('/reports/purchases-vendors', methods=['GET', 'POST'])
@login_required
def purchases_vendors():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
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
    return render_template('admin/purchases-vendors.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases By Vendors', vendors=vendors,avatar=current.get('avatar'))

# inventory - product sales
@admin_bp.route('/reports/purchases-items', methods=['GET', 'POST'])
@login_required
def purchases_items():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find({
            "product_id": request.json["product_id"]
        }, {
            "_id": 0
        })
        return jsonify({"report": list(result)})
    products = db.Products.find()
    return render_template('admin/purchases-items.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases by Items', products=products,avatar=current.get('avatar'))

# inventory - purchase bills
@admin_bp.route('/reports/purchases-bills', methods=['GET', 'POST'])
@login_required
def purchases_bills():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/purchases-bills.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases by Bills',avatar=current.get('avatar'))

# inventory - purchase balance
@admin_bp.route('/reports/purchases-balance', methods=['GET', 'POST'])
@login_required
def purchases_balance():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/purchases-balance.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Vendor Balance',avatar=current.get('avatar'))

# inventory - product sales
@admin_bp.route('/reports/purchases-payments', methods=['GET', 'POST'])
@login_required
def purchases_payments():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/purchases-payments.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Purchases by Payments',avatar=current.get('avatar'))

# inventory - product sales
@admin_bp.route('/reports/inventory-fifo', methods=['GET', 'POST'])
@login_required
def inventory_fifo():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/inventory-fifo.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='FIFO',avatar=current.get('avatar'))

# inventory - product sales
@admin_bp.route('/reports/inventory-valuation', methods=['GET', 'POST'])
@login_required
def inventory_valuation():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/inventory-valuation.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Inventory Valuation',avatar=current.get('avatar'))

# inventory - product sales
@admin_bp.route('/reports/inventory-details', methods=['GET', 'POST'])
@login_required
def inventory_details():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/inventory-details.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Inventory Details',avatar=current.get('avatar'))

# inventory - product sales
@admin_bp.route('/reports/inventory-sales', methods=['GET', 'POST'])
@login_required
def inventory_sales():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find({}, {
            "_id": 0
        })
        return jsonify({"report": list(result)})
    return render_template('admin/inventory-sales.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Product Sales',avatar=current.get('avatar'))

# inventory - order history
@admin_bp.route('/reports/inventory-purchases', methods=['GET', 'POST'])
@login_required
def inventory_purchases():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/inventory-purchases.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Active Purchases',avatar=current.get('avatar'))

# sales -
@admin_bp.route('/reports/sales-item', methods=['GET', 'POST'])
@login_required
def sales_item():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/sales-item.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Items',avatar=current.get('avatar'))

# inventory - product sales
@admin_bp.route('/reports/salesman', methods=['GET', 'POST'])
@login_required
def salesman():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/salesman.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Salesman',avatar=current.get('avatar'))

# inventory - product sales
@admin_bp.route('/reports/sales-balance', methods=['GET', 'POST'])
@login_required
def sales_balance():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/sales-balance.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Balance',avatar=current.get('avatar'))

# sales - packing history
@admin_bp.route('/reports/sales-packing', methods=['GET', 'POST'])
@login_required
def sales_packing():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/sales-packing.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Packing',avatar=current.get('avatar'))

# sales - payment history
@admin_bp.route('/reports/sales-payments', methods=['GET', 'POST'])
@login_required
def sales_payments():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/sales-payments.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Payments',avatar=current.get('avatar'))

# sales - invoice history
@admin_bp.route('/reports/sales-customers', methods=['GET', 'POST'])
@login_required
def sales_customers():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/sales-customers.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Customer',avatar=current.get('avatar'))

# sales - sales orders
@admin_bp.route('/reports/sales-orders', methods=['GET', 'POST'])
@login_required
def sales_orders():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/sales-orders.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Order',avatar=current.get('avatar'))

# sales - sales product
@admin_bp.route('/reports/sales-invoice', methods=['GET', 'POST'])
@login_required
def sales_invoice():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    if request.method == 'POST':
        result = db.Orders.find(
            { "status": { "$in": [ "Await shipping", "Not approved" ] } },
            { "_id": 0 })
        return jsonify({"report": list(result)})
    return render_template('admin/sales-invoice.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Sales Invoices',avatar=current.get('avatar'))

# integrations
@admin_bp.route('/integrations', methods=['GET', 'POST'])
@login_required
def integrations():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    print("----------------------------- bread_crumb:", bread_crumb['Integrations'])
    return render_template('admin/integrations.html', breadCrumb=BREAD_CRUMB['Integrations'][0],
    uname=current_user.get_id(), title='Integrations',avatar=current.get('avatar'))

# reports
@admin_bp.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    return render_template('admin/reports.html', breadCrumb=BREAD_CRUMB['Reports'][0],
    uname=current_user.get_id(), title='Report',avatar=current.get('avatar'))

# billing
@admin_bp.route('/billing', methods=['GET', 'POST'])
@login_required
def billing():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    return render_template('admin/billing.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Billing',avatar=current.get('avatar'))

@admin_bp.route('/makeorder', methods=['GET', 'POST'])
def makeorder():
    print(request.json)
    for x in request.json['products']:
        product = db.Products.find_one({"id": x['product_id']})
        new_order = {
            'order_id': str(uid()),
            'player_id': request.json['player_id'],
            'product_id': product['id'],
            'product_name': product['product'],
            'group_id': product['category'],
            'subgroup': product['subgroup'],
            'quantity': x['quantity'],
            'type': 'store',
            'price': product['price'],
            'street': request.json['street'],
            'city' : request.json['city'],
            'state' : request.json['state'],
            'zip' : request.json['zip'],
            'country': 'US',
            'ship_id': None,
            'invoice_id': None,
            'date': datetime.now(),
            'status': 'Not approved'
        }
        db.Orders.insert_one(new_order)

        db.Queue.insert_one(new_order)
        new_hist_item = {
            'id' : str(uid()),
            'pid' : x['product_id'],
            'type' : 'ITEM',
            'date' : date.today().strftime('%Y/%m/%d'),
            'reason' : "Bought " + x['quantity'] + " " + product['product'],
            'adjustments' : new_item['id'],
            'description' : "User ID: "+ current_user.get_id()
        }
        db.History.insert_one(new_hist_item)
    return json.dumps({"success": "success"})

# checkout
@admin_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():

    ######################################
    ### Adding Cart
    ######################################
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    cartData = request.form.get('cart-data')
    # when carts is empty
    if cartData == '':
        return render_template('admin/checkout.html', title='Checkout', groups=groupsList, ordersByProduct=[], total={"count": 0, "price": 0})

    # when carts has some products
    print("-------go to checkout page-------------")
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
    return render_template('admin/checkout.html', title='Checkout',groups=groupsList, ordersByProduct=ordersByProduct, total=total)
# exports
@admin_bp.route('/files', methods=['GET', 'POST'])
@login_required
def files():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    return render_template('admin/files.html', breadCrumb=BREAD_CRUMB['Orders'][0],
    uname=current_user.get_id(), title='Files')

# contacts
@admin_bp.route('/contacts', methods=['GET', 'POST'])
@login_required
def contacts():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    return render_template('admin/contacts.html', breadCrumb=BREAD_CRUMB['Shipping'][0],
    uname=current_user.get_id(), title='Contacts',avatar=current.get('avatar'))

# Orders
@admin_bp.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    tblOrdrs = []
    table = db.Orders.find()
    for ordr in table:
        uid = ordr['player_id']
        pname = ""
        plyr = db.Users.find_one({'id':uid})
        if plyr:
            pname = plyr['name']
        else :
            pname = "Unknown guest"

        iname = ""
        if 'item_id' in ordr:
            iid = ordr['item_id']
            itm = db.Products.find_one({'id':iid})
            if itm:
                iname = itm['product']
        #print("--- prdt: ",prdt,", cid: ",cid,", cname: ",cname,", vname: ",vname)

        tblOrdrs.append({ #Variable 'table' is just iterator, so it indicates the NULL after finished loop
            'order_id': ordr['order_id'],
            'player': ordr['player_id'],
            'item': ordr['product_name'],
            'quantity': ordr['quantity'],
            'type': ordr['type'],
            'price': ordr['price']
        })

    return render_template('admin/orders.html', breadCrumb=BREAD_CRUMB['Orders'][0], uname=current_user.get_id(), title='Queue', table=tblOrdrs,avatar=current.get('avatar'))

@admin_bp.route('/orders/delete/<string:item>', methods=['GET', 'POST'])
@login_required
def delete_order(item):
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    new_order = db.Queue.find_one({'order_id':item})
    if new_order != None:
        db.Queue.remove({'order_id': item})
    db.Orders.remove({'order_id': item})
    return redirect(url_for('admin.orders'))

# Queue
@admin_bp.route('/queue', methods=['GET', 'POST'])
@login_required
def queue():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    # current = db.Queue.find()

    queue = db.Queue.find()
    return render_template('admin/queue.html', breadCrumb=BREAD_CRUMB['Queue'][0],
    uname=current_user.get_id(), title='Queue', queue=queue, qlen=queue.count(),avatar=current.get('avatar'))

@admin_bp.route('/queue/approve/<string:item>', methods=['GET', 'POST'])
@login_required
def approve(item):
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    db.Queue.remove({'order_id':item})
    db.Orders.update({'order_id': item},{"$set": {'status' : 'Await shipping'}})
    return redirect(url_for('admin.queue'))

@admin_bp.route('/queue/disapprove/<string:item>', methods=['GET', 'POST'])
@login_required
def disapprove(item):
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    db.Queue.remove({'order_id':item})
    db.Orders.remove({'order_id': item})
    return redirect(url_for('admin.queue'))

# profile page
# 2019-6-17 midas
@admin_bp.route('/myprofile', methods=['GET', 'POST'])
@login_required
def myprofile():
    user = db.Users.find_one({'id':current_user.username})
    data = {
        'id': user['id'],
        'name': user['name'],
        'email': user['email']
    }

    avatar = user.get('avatar')

    if request.method == 'POST':
        if request.form["password"] == "":
            newdata = {
                'id': request.form["username"] if request.form["username"] else user['id'],
                'name': request.form['name'] if request.form["name"] else user['name'],
                'email': request.form['email'] if request.form["email"] else user['email'],
                'avatar': request.form['hdfiles'] if request.form["hdfiles"] else user.get('avatar')
            }
        else:
            pw = request.form["password"]
            newdata = {
                'id': request.form["username"] if request.form["username"] else user['id'],
                'name': request.form['name'] if request.form["name"] else user['name'],
                'email': request.form['email'] if request.form["email"] else user['email'],
                'pw' : User.setHash(pw),
                'avatar': request.form['hdfiles'] if request.form["hdfiles"] else user.get('avatar')
            }
        db.Users.update_one(
            {"_id": user['_id']},
            {"$set": newdata})
        data = {
            'id': newdata['id'],
            'name': newdata['name'],
            'email': newdata['email']
        }

        avatar = newdata.get('avatar')

    historys = db.History.find({ "description": "User ID: "+current_user.get_id() }, {"_id":0}).sort('date',-1)
    historyData = []
    for history in historys:
        historyData.append(history)

    return render_template('admin/profile.html', breadCrumb=BREAD_CRUMB['Profile'][0], historys = historyData, title='Profile',uname=current_user.get_id(), data=data, avatar=avatar)

# signup page
@admin_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        return redirect(url_for('admin.home'))
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = {
            'id': form.username.data,
            'name':form.name.data,
            'uid': User.setUID(),
            'email':form.email.data,
            'pw': User.setHash(form.pw.data),
            'admin': True
        }
        db.Users.insert_one(new_user)
        flash('Congratulations {}, you are now a registered user!'.format(form.name.data))
        return redirect(url_for('admin.home'))
    return render_template('admin/signup.html', breadCrumb=BREAD_CRUMB['Signup'][0], title='Register', form=form)

@admin_bp.route('/8f9wehf38jd', methods=['GET', 'POST'])
def createsuperuser():
    new_user = {
        'id': "admin",
        'name': "admin",
        'uid': "admin",
        'email': "admin@admin.com",
        'pw': User.setHash("admin"),
        "role": "admin"
    }
    db.Users.insert_one(new_user)
    return redirect(url_for('admin.login'))

# login page
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    print("++++++++++      login     +++++++++++")
    if current_user.is_authenticated:
        return redirect(url_for('admin.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.Users.find_one({'id':form.username.data})
        if user != None and User.checkPassword(user['pw'], form.pw.data):
            verify = User(user['id'])
            login_user(verify)
            return redirect(url_for('admin.home'))
        flash('Invalid Username or Password. Please try again.')
        return redirect(url_for('admin.login'))
    return render_template('admin/login.html', breadCrumb=BREAD_CRUMB['Login'][0], title='Login', form=form)

# logout
@admin_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/uploads/<path:path>', methods=['GET', 'POST'])
def send_images(path):
    return send_from_directory('uploads', path)

@admin_bp.route('/faq', methods=['GET', 'POST'])
def faq():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/faq.html', groups=groupsList, title='FAQ')

@admin_bp.route('/affiliate', methods=['GET', 'POST'])
def affiliate():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/affiliate.html', groups=groupsList, title='Affiliate')

@admin_bp.route('/payments', methods=['GET', 'POST'])
def payments():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/payments.html', groups=groupsList, title='Payments')

@admin_bp.route('/privacy', methods=['GET', 'POST'])
def privacy():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/privacy.html', groups=groupsList, title='Privacy')

@admin_bp.route('/about', methods=['GET', 'POST'])
def about():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/about.html', groups=groupsList, title='About')

@admin_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/contact.html', groups=groupsList, title='Contact')

@admin_bp.route('/returns', methods=['GET', 'POST'])
def returns():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/returns.html', groups=groupsList, title='Returns')

@admin_bp.route('/terms', methods=['GET', 'POST'])
def terms():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/terms.html', groups=groupsList, title='Terms & Conditions')

@admin_bp.route('/copyright', methods=['GET', 'POST'])
def copyright():
    groups = db.Groups.aggregate(
        [
            { "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }
        ]
    )
    groupsList = {}
    for x in groups:
        groupsList[x['_id']] = x['store']
    return render_template('admin/copyright.html', groups=groupsList, title='Copyright')

# home page
# @admin_bp.route('/store_login', methods=['GET', 'POST'])
# def store_login():
#     if current_user.is_authenticated:
#         user_id = current_user.get_id()
#         current = db.Users.find_one({"id": user_id})
#         return redirect(url_for('admin.accounts'))

#     groupsList = {}
#     groups = db.Groups.aggregate(
#         [{ "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }]
#     )
#     for x in groups:
#         groupsList[x['_id']] = x['store']

#     form = StoreLoginForm()
#     if form.validate_on_submit():
#         user = db.Users.find_one({'id':form.email.data})
#         if user != None and User.checkPassword(user['pw'], form.pw.data):
#             verify = User(user['id'])
#             login_user(verify)
#             return redirect(url_for('admin.accounts'))
#         flash('Invalid Username or Password. Please try again.')
#         return redirect(url_for('admin.store_login'))
#     return render_template(
#         'admin/store-login.html',
#         title='Store Login',
#         groups=groupsList,
#         form=form
#         )

# # home page
# @admin_bp.route('/store_signup', methods=['GET', 'POST'])
# def store_signup():
#     if current_user.is_authenticated:
#         user_id = current_user.get_id()
#         current = db.Users.find_one({"id": user_id})
#         return redirect(url_for('admin.accounts'))

#     groupsList = {}
#     groups = db.Groups.aggregate(
#         [{ "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }]
#     )
#     for x in groups:
#         groupsList[x['_id']] = x['store']

#     form = StoreSignupForm()
#     if form.validate_on_submit() and User.validate_email(form.email.data):
#         new_user = {
#             'id': form.email.data,
#             'first':form.first.data,
#             'uid': User.setUID(),
#             'last':form.last.data,
#             'pw': User.setHash(form.pw.data),
#             'orders': [],
#             'returns': [],
#             'balance': 0,
#             'admin': False,
#             'address': None,
#             'address2': None,
#             'cardType': None,
#             'cardHide': None,
#             'cardName': None,
#             'cardNumber': None,
#             'cardDate': None,
#             'city': None,
#             'state': None,
#             'zip': None,
#             'phone': None,
#             'emailNotification':False,
#             'emailFlash':False,
#             'emailProducts':False,
#             'emailSeller':False,
#             'emailProduct':False,
#             'emailSpecial':False,
#             'phoneNotification':False,
#             'phoneAlerts':False,
#             'phoneShipment':False,
#             'joined': date.today()
#         }
#         db.Users.insert_one(new_user)
#         flash('Congratulations {}, you are now a registered user!'.format(form.first.data))
#         return redirect(url_for('admin.store_login'))
#     return render_template(
#         'admin/store-signup.html',
#         title='Store Signup',
#         groups=groupsList,
#         form=form,
#         )

# home page
@admin_bp.route('/accounts', methods=['GET', 'POST'])
@login_required
def accounts():
    current = db.Users.find_one({"id": current_user.get_id()})
    products = db.Products.find()
    print(current_user)
    print(dir(current_user))

    groupsList = {}
    groups = db.Groups.aggregate(
        [{ "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }]
    )
    for x in groups:
        groupsList[x['_id']] = x['store']

    form = CouponForm()
    if form.validate_on_submit():
        user = current

        if form.coupon.data:
            user['balance'] += 10
            db.Users.update({'id':current['id']},{"$set":user})

    return render_template(
        'admin/accounts.html',
        title='Store',
        groups=groupsList,
        current=current,
        form=form
        )

# home page
@admin_bp.route('/account-settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    current = db.Users.find_one({"id": current_user.get_id()})
    form = SettingsForm()

    if form.validate_on_submit():
        user = current

        if form.first.data:
            user['first'] = form.first.data
        if form.last.data:
            user['last'] = form.last.data
        if form.pw.data:
            user['pw'] = User.setHash(form.pw.data)
        db.Users.update({'id':current['id']},{"$set":user})

    groupsList = {}
    groups = db.Groups.aggregate(
        [{ "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }]
    )
    for x in groups:
        groupsList[x['_id']] = x['store']

    return render_template(
        'admin/account-settings.html',
        title='Settings',
        groups=groupsList,
        current=current,
        form=form
        )

# home page
@admin_bp.route('/account-payments', methods=['GET', 'POST'])
@login_required
def account_payments():
    current = db.Users.find_one({"id": current_user.get_id()})
    form = UpdatePaymentsForm()

    groupsList = {}
    groups = db.Groups.aggregate(
        [{ "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }]
    )
    for x in groups:
        groupsList[x['_id']] = x['store']

    if form.validate_on_submit():
        user = current

        if form.card.data and form.card.data != 'None':
            user['card'] = form.card.data
        if form.cardNumber.data:
            user['cardNumber'] = form.cardNumber.data
            user['cardHide'] = form.cardNumber.data[-4:]
        if form.cardName.data:
            user['cardName'] = form.cardName.data
        if form.cardMonth.data and form.cardMonth.data != 'None':
            user['cardMonth'] = form.cardMonth.data
        if form.cardYear.data and form.cardYear.data != 'None':
            user['cardYear'] = form.cardYear.data
        if form.address.data:
            user['address'] = form.address.data
        if form.address2.data:
            user['address2'] = form.address2.data
        if form.city.data:
            user['city'] = form.city.data
        if form.state.data and form.state.data != 'None':
            user['state'] = form.state.data
        if form.zip.data:
            user['zip'] = form.zip.data
        if form.phone.data:
            user['phone'] = form.phone.data

        db.Users.update({'id':current['id']},{"$set":user})

    return render_template(
        'admin/account-payments.html',
        title='Store',
        groups=groupsList,
        form=form,
        current=current
        )

# home page
@admin_bp.route('/account-returns', methods=['GET', 'POST'])
@login_required
def account_returns():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    products = db.Products.find()

    groupsList = {}
    groups = db.Groups.aggregate(
        [{ "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }]
    )
    for x in groups:
        groupsList[x['_id']] = x['store']

    form = UpdatePaymentsForm()

    return render_template(
        'admin/account-returns.html',
        title='Returns',
        groups=groupsList,
        form=form
        )

# home page
@admin_bp.route('/account-email', methods=['GET', 'POST'])
@login_required
def account_email():
    current = db.Users.find_one({"id": current_user.get_id()})
    form = EmailForm()

    groupsList = {}
    groups = db.Groups.aggregate(
        [{ "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }]
    )
    for x in groups:
        groupsList[x['_id']] = x['store']

    if form.validate_on_submit():
        user = current

        user['newsletter'] = form.newsletter.data
        user['deals'] = form.deals.data
        user['rating'] = form.rating.data
        user['seller'] = form.seller.data
        user['voting'] = form.voting.data
        user['offers'] = form.offers.data

        if form.unsubscribe.data:
            user['newsletter'] = False
            user['deals'] = False
            user['rating'] = False
            user['seller'] = False
            user['voting'] = False
            user['offers'] = False

        db.Users.update({'id':current['id']},{"$set":user})

    return render_template(
        'admin/account-email.html',
        title='Email',
        groups=groupsList,
        form=form,
        current=current
        )

# home page
@admin_bp.route('/account-text', methods=['GET', 'POST'])
@login_required
def account_text():
    current = db.Users.find_one({"id": current_user.get_id()})
    form = TextForm()

    groupsList = {}
    groups = db.Groups.aggregate(
        [{ "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }]
    )
    for x in groups:
        groupsList[x['_id']] = x['store']

    if form.validate_on_submit():
        user = current

        if form.phone.data:
            user['phone'] = form.phone.data
        user['auto'] = form.auto.data
        user['alert'] = form.alert.data
        user['shipment'] = form.shipment.data

        if form.unsubscribe.data:
            user['auto'] = False
            user['alert'] = False
            user['shipment'] = False

        db.Users.update({'id':current['id']},{"$set":user})

    return render_template(
        'admin/account-text.html',
        title='Text',
        groups=groupsList,
        current=current,
        form=form
        )

# home page
@admin_bp.route('/account-orders', methods=['GET', 'POST'])
@login_required
def account_orders():
    user_id = current_user.get_id()
    current = db.Users.find_one({"id": user_id})
    products = db.Products.find()

    groupsList = {}
    groups = db.Groups.aggregate(
        [{ "$group" : { "_id" : "$type", "store": { "$push": "$$ROOT" } } }]
    )
    for x in groups:
        groupsList[x['_id']] = x['store']

    return render_template(
        'admin/account_orders.html',
        title='Text',
        groups=groupsList,
        )
