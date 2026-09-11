from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# ==========================
# Category Model
# ==========================
class Category(models.Model):

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ==========================
# Product Model
# ==========================
class Product(models.Model):

    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.CASCADE
    )

    created_by = models.ForeignKey(
        User,
        related_name="products",
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)

    slug = models.SlugField(max_length=255, unique=True)

    author = models.CharField(
        max_length=255,
        default="Admin"
    )

    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    in_stock = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    views_count = models.PositiveIntegerField(default=0)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Products"
        ordering = ["-created"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "store:product_detail",
            args=[self.slug]
        )


# ==========================
# Product Images
# ==========================
class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to="products/",
    blank=True,
    null=True
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True
    )

    is_feature = models.BooleanField(
        default=False
    )

    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name_plural = "Product Images"

    def __str__(self):
        return f"{self.product.title} Image"


# ==========================
# Order Model
# ==========================
import uuid

class Order(models.Model):
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(
        User,
        related_name="orders",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    payment_method = models.CharField(max_length=50, default="bank")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=200.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order #{self.order_number} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)


# ==========================
# OrderItem Model
# ==========================
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name="order_items",
        on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product.title} (Order #{self.order.order_number})"

    def get_total_price(self):
        return self.price * self.quantity