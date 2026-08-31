from django.shortcuts import render, get_object_or_404 
from django.http import JsonResponse

from store.models import Product
from .basket import Basket

def basket_summary(request):
    basket = Basket(request)
    return render(request, 'store/basket/summary.html', {'basket': basket})

def basket_add(request):
    basket = Basket(request)

    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        product_qty = int(request.POST.get('productqty'))

        product = get_object_or_404(Product, id=product_id)
        basket.add(product=product, qty=product_qty)

        # Get first image
        first_image = product.images.first()
        image_url = ""
        if first_image:
            image_url = first_image.image.url

        return JsonResponse({
            'qty': len(basket),
            'product': product.title,
            'price': str(product.price),
            'image': image_url,
            'productqty': product_qty,
            'subtotal': str(basket.get_subtotal()),
            'shipping': str(basket.get_shipping_price()),
            'tax': str(basket.get_tax()),
            'total': str(basket.get_total_price()),
            'items': basket.get_items_data(),
        })

def basket_update(request):
    basket = Basket(request)

    if request.POST.get("action") == "post":
        product_id = request.POST.get("productid")
        qty = int(request.POST.get("productqty"))

        basket.update(product_id, qty)

        return JsonResponse({
            "qty": len(basket),
            "subtotal": str(basket.get_subtotal()),
            "shipping": str(basket.get_shipping_price()),
            "tax": str(basket.get_tax()),
            "total": str(basket.get_total_price()),
            "items": basket.get_items_data(),
        })

def basket_delete(request):
    basket = Basket(request)

    if request.POST.get("action") == "post":
        product_id = request.POST.get("productid")
        basket.delete(product_id=product_id)

        return JsonResponse({
            "qty": len(basket),
            "subtotal": str(basket.get_subtotal()),
            "shipping": str(basket.get_shipping_price()),
            "tax": str(basket.get_tax()),
            "total": str(basket.get_total_price()),
            "items": basket.get_items_data(),
        })

def checkout(request):
    basket = Basket(request)
    return render(
        request,
        "store/checkout.html",
        {"basket": basket}
    )

def billing(request):
    basket = Basket(request)
    return render(
        request,
        "store/billing.html",
        {"basket": basket}
    )