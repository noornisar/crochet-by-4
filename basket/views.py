import logging
from django.shortcuts import render, redirect, get_object_or_404 
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages

from store.models import Product, Order, OrderItem
from store.services.email_service import send_order_confirmation_email
from .basket import Basket

logger = logging.getLogger('store')

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
    if len(basket) == 0:
        return redirect('store:shop')

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        full_name = f"{first_name} {last_name}".strip()
        if not full_name and request.user.is_authenticated:
            full_name = request.user.get_full_name() or request.user.username

        email = request.POST.get("email", "").strip()
        if not email and request.user.is_authenticated:
            email = request.user.email

        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()
        payment_method = request.POST.get("payment_method", "bank").strip() or "bank"

        current_data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'phone': phone,
            'address': address,
            'city': city,
            'postal_code': postal_code,
            'payment_method': payment_method,
        }

        if not email:
            messages.error(request, "Please enter your contact email address before placing your order.")
            return render(request, "store/checkout.html", {"basket": basket, "checkout_info": current_data})

        if not address or not city or not phone:
            messages.error(request, "Please complete your phone number, street address, and city.")
            return render(request, "store/checkout.html", {"basket": basket, "checkout_info": current_data})

        # 1. Create the Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name or "Valued Customer",
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            payment_method=payment_method,
            subtotal=basket.get_subtotal(),
            shipping_cost=basket.get_shipping_price(),
            tax=basket.get_tax(),
            total_price=basket.get_total_price(),
        )

        # 2. Create OrderItems from basket
        for item in basket:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['qty']
            )

        # 3. Safely send Order Confirmation Email (Never crashes the order)
        host = request.get_host()
        try:
            current_site = get_current_site(request)
            domain = current_site.domain if (current_site and current_site.domain != 'example.com') else host
        except Exception:
            domain = host or '127.0.0.1:8000'

        try:
            sent, err = send_order_confirmation_email(order, site_domain=domain)
            if not sent:
                logger.warning(f"Customer confirmation email was not sent for order #{order.order_number}: {err}")
        except Exception as e:
            logger.error(f"Failed to send confirmation email for order #{order.id}: {e}")

        # 4. Clear the basket and checkout session
        basket.clear()
        if 'checkout_info' in request.session:
            del request.session['checkout_info']

        # 5. Redirect directly to dedicated order confirmation page
        return redirect("basket:order_confirmation", order_number=order.order_number)

    checkout_info = request.session.get('checkout_info', {})
    return render(
        request,
        "store/checkout.html",
        {"basket": basket, "checkout_info": checkout_info}
    )

def billing(request):
    """Redirect to unified single-page checkout."""
    return redirect("basket:checkout")


def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "store/order_success.html", {"order": order})