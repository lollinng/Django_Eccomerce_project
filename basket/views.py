from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from store.models import Product
from .basket import Basket

# Create your views here.

# render cart/basket page
def basket_summary(request):
    basket = Basket(request)
    return render(request,'basket/summary.html',{'basket':basket})


def basket_add(request):
    basket = Basket(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))
        product = get_object_or_404(Product,id=product_id)
         
        basket.add(product=product,qty=product_qty)  
        
        # sending response back to ajax query from single.html for basket icon
        basketqty = basket.__len__()
        response = JsonResponse({'qty':basketqty})
        return response

def basket_delete(request):
    basket = Basket(request)

    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        basket.delete(product=product_id)

        basketqty = basket.__len__()
        basketsubtotal = basket.get_subtotal_price()
        baskettotal = basket.get_total_price()
        response = JsonResponse({'qty': basketqty,'subtotal': basketsubtotal,'total':baskettotal})
        return response
    
def basket_update(request):
    basket = Basket(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))
        basket.update(product=product_id,qty=product_qty)

        prod_total = str(basket.get_prod_price(product=product_id))
        basketqty = basket.__len__()
        baskettotal = basket.get_total_price() 
        basketsubtotal = basket.get_subtotal_price()
        response = JsonResponse({'qty': basketqty, 'subtotal': basketsubtotal,'total':baskettotal,'prod_total':prod_total})
        return response
    



       