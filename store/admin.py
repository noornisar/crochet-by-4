from django.contrib import admin
from .models import Category, Product, ProductImage


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


admin.site.register(Category)