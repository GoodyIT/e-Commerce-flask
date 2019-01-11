from pymongo import MongoClient
from uuid import uuid4 as uid
from random import randint as rand

''' Shell Script to Creates Pseudo Orders for Python Mongo '''

# Connect to DB
client = MongoClient('mongodb://localhost:27017/')
db = client.test_inv

def createQueues(count):
    types = ['app', 'store']
    orders = []

    while count > 0:
        order = {
            'order_id': str(uid()),
            'player_id': str(uid()),
            'item_id': str(uid()),
            'quantity': rand(1, 10),
            'type': types[rand(0,1)],
            'price': rand(1, 100),
            }
        orders.append(order)
        count -= 1

    for x in orders:
        db.Queue.insert_one(x)
    return

def createOrders(count):
    types = ['app', 'store']
    orders = []

    while count > 0:
        order = {
            'order_id': str(uid()),
            'player_id': str(uid()),
            'item_id': str(uid()),
            'quantity': rand(1, 10),
            'type': types[rand(0,1)],
            'price': rand(1, 100),
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
        except:
            print("Not a valid option.")

        if selection == 1 and amount > 0:
            createQueues(amount)
            break
        elif selection == 2 and amount > 0:
            createOrders(amount)
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
