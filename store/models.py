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