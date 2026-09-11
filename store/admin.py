from django.contrib import admin
from .models import Category, Product, ProductImage, Order, OrderItem


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "price",
        "in_stock",
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    inlines = [
        ProductImageInline,
    ]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ['product']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'full_name',
        'email',
        'phone',
        'payment_method',
        'total_price',
        'is_paid',
        'created',
    )
    list_filter = ('is_paid', 'payment_method', 'created')
    search_fields = ('order_number', 'full_name', 'email', 'phone')
    inlines = [OrderItemInline]


admin.site.register(Category)