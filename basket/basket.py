from decimal import Decimal
from store.models import Product


class Basket():
    """
    A base Basket class , providing some default behaviors that 
    can be inherited or overrided , as necessary
    """

    def __init__(self,request):
        self.session = request.session
        basket = self.session.get('skey')

        # if user new create/build skey basket data/session
        if 'skey' not in request.session:
            basket = self.session['skey'] = {}
        self.basket = basket


    def add(self,product,qty): 
        """
        Adding and updating the users basket session data
        """
        product_id = product.id
        
        # if product doesn't exist add the product price
        if product_id not in self.basket:
            self.basket[product_id] = {
                'price' : str(product.price),
                'qty': int(qty)
            }

        
        # expilictly tell django to update the session
        self.session.modified = True

    def __len__(self):
        """
        Get the basket data and count the qty of items

        We iterator through items and add quantity in the list to extract the whole sum from list
        """
        return sum(item['qty'] for item in self.basket.values())
    
    # returns a iterable object
    def __iter__(self):
        """
        collect the product_id in the session data to query the db and return products
        """
        # all the product ids inside basket
        product_ids = self.basket.keys() 

        # filter out the basket products from the db
        products = Product.products.filter(id__in=product_ids)
        basket  = self.basket.copy()
        
        # adding product object and id to a nested dictionary
        # containing product id as index 
        # and dict of product_obj,qty and price as nested values 
        for product in products:
            basket[str(product.id)]['product'] = product

        # creating a new field in basket nested dict
        for item in basket.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['qty']
            # yield returns a generated object instead of returning a simple value 
            yield item
    
    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['qty'] for item in self.basket.values()
        )
    