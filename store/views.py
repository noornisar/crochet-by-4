from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch

# Create your views here.
from .models import Category, Product


def categories(request):
    return{
        'categories': Category.objects.all()
    }

def all_products(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products}) # reder is for loading templates

def product_detail(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug
    )

    return render(
        request,
        'store/product_detail.html',
        {'product': product}
    )
from .models import Category

def shop(request):

    categories = Category.objects.prefetch_related(
        "products__images"
    ).all()

    return render(
        request,
        "store/shop.html",
        {
            "categories": categories
        }
    )
