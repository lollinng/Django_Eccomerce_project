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
            self.basket[product_id] = {'price':str(product.price),'qty':int(qty)}

        
        # expilictly tell django to update the session
        self.session.modified = True

    def __len__(self):
        """
        Get the basket data and count the qty of items

        We iterator through items and add quantity in the list to extract the whole sum from list
        """
        return sum(item['qty'] for item in self.basket.values())
    
