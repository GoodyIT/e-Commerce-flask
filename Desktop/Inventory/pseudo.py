from pymongo import MongoClient
from uuid import uuid4 as uid
from datetime import datetime
import random, pandas

''' Shell Script to Creates Pseudo Orders for Python Mongo '''

# Connect to DB
client = MongoClient('mongodb://localhost:27017/')
db = client.test_inv

def _removeNewLine(input):
    ''' Removes \n from string elements '''
    if input.endswith('\n'):
        return input[0:len(input)-1]
    return input

def _getDate(input=2017):
    ''' Function will return a random datetime between two datetime
    objects. '''
    year = random.choice(range(input, 2018))
    month = random.choice(range(1, 12))
    if month == 2:
        day = random.choice(range(1, 28))
    else:
        day = random.choice(range(1, 30))
    return datetime(year, month, day)

def _getCity():
    ''' Returns a City from CSV '''
    df = pandas.read_csv('uscities.csv')
    return df['city'][random.randint(0,len(df['city']))]

def _getState():
    ''' Returns a City from CSV '''
    df = pandas.read_csv('uscities.csv')
    return df['state_id'][random.randint(0,len(df['state_id']))]

def _getZip():
    ''' Returns a City from CSV '''
    df = pandas.read_csv('uscities.csv')
    return df['zips'][random.randint(0,len(df['zips']))]

def _street():
    ''' Generates a address based around called names from streetNames.txt
    file '''
    ENDING = ['court', 'street', 'grove', 'avenue', 'place']
    NUMBER = random.randint(1, 5000)
    names = None

    with open('streetNames.txt') as f:
        names = f.readlines()
    choice = random.choice(names)
    return '{} {} {}'.format(str(NUMBER), _removeNewLine(choice), random.choice(ENDING))

def createQueues(count, year):
    ''' Generates a Queue based on inputting values '''
    types = ['app', 'store']
    queues = []
    products = db.Products.find({})
    while count > 0:
        product_num = random.randint(0, db.Products.count_documents({})-1)
        product_id  = products[product_num]['id']
        group_id    = products[product_num]['category']
        subgroup    = products[product_num]['subgroup']
        product_name= products[product_num]['product']
        order = {
            'order_id': str(uid()),
            'player_id': str(uid()),
            'product_id': product_id,
            'product_name': product_name,
            'group_id': group_id,
            'subgroup': subgroup,
            'quantity': random.randint(1, 10),
            'type': types[random.randint(0,1)],
            'price': random.randint(1, 100),
            'street': _street(),
            'city' : _getCity(),
            'state' : _getState(),
            'zip' : _getZip(),
            'country': 'US',
            'date': _getDate(year)
            }
        queues.append(order)
        count -= 1

    for x in queues:
        db.Queue.insert_one(x)
    return

def createOrders(count, year):
    types = ['app', 'store']
    orders = []
    products = db.Products.find({})
    while count > 0:
        product_num = random.randint(0, db.Products.count_documents({})-1)
        product_id  = products[product_num]['id']
        group_id    = products[product_num]['category']
        subgroup    = products[product_num]['subgroup']
        product_name= products[product_num]['product']
        ship_id     = str(uid()) if random.randint(0,1) else None
        invoice_id  = str(uid()) if (random.randint(0, 1) == 1 and ship_id is not None) else None
        order = {
            'order_id': str(uid()),
            'player_id': str(uid()),
            'product_id': product_id,
            'product_name': product_name,
            'group_id': group_id,
            'subgroup': subgroup,
            'quantity': random.randint(1, 10),
            'type': types[random.randint(0,1)],
            'price': random.randint(1, 100),
            'shipped': 'awaiting',
            'street': _street(),
            'city' : _getCity(),
            'state' : _getState(),
            'zip' : _getZip(),
            'country': 'US',
            'ship_id': ship_id,
            'invoice_id': invoice_id,
            'date': _getDate(year)
            }
        orders.append(order)
        count -= 1

    for x in orders:
        db.Orders.insert_one(x)
    return

def main():
    # Get User choices
    while True:
        print("1. Queues | 2. Orders")
        selection, amount = 0, 0

        try:
            selection = int(input("Please enter your choice: "))
            amount = int(input("Please enter how many records you want: "))
            year = int(input("Enter a year for what how long the dates will go back to: "))
        except:
            print("Not a valid option.")

        if selection == 1 and amount > 0:
            createQueues(amount, year)
            break
        elif selection == 2 and amount > 0:
            createOrders(amount, year)
            break
        else:
            print("Not a valid option. Please try again.")



if __name__ == "__main__":
    main()
    while True:
        choice = str(input("More Entries? Y or N: "))
        if choice.lower() == 'y':
            main()
        elif choice.lower() == 'n':
            print("-----Completed-----")
            break
        else:
            print("Invalid Entry.")
