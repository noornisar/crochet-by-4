from django.urls import path 
from .models import Category
from . import views 
from django.shortcuts import render

app_name = 'store'

urlpatterns = [
    path('', views.all_products, name='all_products'), 
    path('shop/', views.shop, name='shop'),

   
  
    path(
        'product/<slug:slug>/',
        views.product_detail,
        name='product_detail'
    ),
]
def shop(request):

    categories = Category.objects.prefetch_related('products').all()

    return render(
        request,
        "store/shop.html",
        {
            "categories": categories
        }
    )