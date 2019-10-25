class Warehouse:
    def __init__(self):
        self.inventory = []
        self.pending = []
        self.completed = []

    def _getUID(self):
        ''' Creates a Unique Identification Number. Returns in STR Format
        '''
        temp = uid()
        return temp.__str__()

    def search_items(self, id):
        '''
        searches items in self.inventory
        id = id of item (type: str)
        '''
        for x in self.inventory:
            if x['id'] == id:
                return True
        return False

    def add_item(self, id, price, shipping, company=None, url=None):
        '''
        id = item id number (type:str)
        price = price of item (type:float)
        shipping = list of available shipping (type:list)
        company = company that items are being orderd (type:str)
        url = url of site (type:str)
         '''
        if not search_items(id):
            items = {}
            items['id'] = id
            items['in_stock'] = False
            items['status'] = None
            items['quantity'] = None
            items['SKU'] = None
            items['date_added'] = str(date.today().time())
            items['price'] = price
            items['company'] = company
            items['currency'] = None
            items['url'] = url
            items['catalog'] = catalog
            items['international'] = False
            items['shipping'] = shipping
            self.inventory.append(items)
            return items
        return False

    def delete_item(self, id):
        '''
        Deletes order from self.inventory.
        id = id of item (type: str)
        '''
        if search_items(id):
            for x in self.inventory:
                if x['id'] == id:
                    self.inventory.remove(x)
            return True
        return False

    def search_order(self, id):
        '''
        searches for order in self.pending
        id = id of order (type: str)
        '''
        for x in self.pending:
            if x['id'] == id:
                return True
        return False

    def create_order(self, user_id, item_id, shipping):
        '''
        Creates a order and places it in queue.
        user_id = id of player making order (type: str)
        item_id = id of item being orderd (type: str)
        shipping = what type of shipping (type: str)
        '''
        order = {}
        order['id']= self._getUID()
        order['user_id'] = user_id
        order['item_id'] = item_id
        order['shipping'] = shipping
        self.pending.append(order)
        return order

    def delete_order(self, id):
        '''
        Deletes order from self.pending queue.
        id = id of order (type: str)
        '''
        if search_order(id):
            for x in order_orders:
                if x['id'] == id:
                    order_orders.remove(x)
            return True
        return False

    def completed_order(self, id):
        '''
        Transfers order from self.pending to self.completed.
        id = id of order (type: str)
        '''
        if search_order(id):
            for x in self.pending:
                if x['id'] == id:
                    self.completed.append(x)
                    self.pending.remove(x)
            return True
        return False
