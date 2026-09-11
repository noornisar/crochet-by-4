from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch, F

# Create your views here.
from .models import Category, Product


def categories(request):
    return{
        'categories': Category.objects.all()
    }

def all_products(request):
    products = Product.objects.filter(is_active=True).prefetch_related('images')
    # Active products with images for the hero auto-scrolling showcase
    scroll_products = Product.objects.filter(
        is_active=True,
        images__isnull=False
    ).distinct().prefetch_related('images').order_by('-views_count', '-created')[:10]
    return render(request, 'store/home.html', {
        'products': products,
        'scroll_products': scroll_products,
    })

def product_detail(request, slug):
    product = get_object_or_404(
        Product,
        slug=slug
    )
    # Increment view count atomically
    Product.objects.filter(id=product.id).update(views_count=F('views_count') + 1)

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

def category_list(request, category_slug=None):
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        categories = Category.objects.filter(id=category.id).prefetch_related("products__images")
    else:
        categories = Category.objects.prefetch_related("products__images").all()
    return render(
        request,
        "store/shop.html",
        {
            "categories": categories
        }
    )


from django.contrib import messages
from .forms import ContactForm
from .services.email_service import send_contact_inquiry_emails


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            success, error = send_contact_inquiry_emails(name, email, subject, message)
            if success:
                messages.success(request, "🌸 Thank you! Your message has been sent successfully. We'll get back to you soon.")
            else:
                messages.warning(request, "Your message was received, but there was a slight delay sending the email confirmation.")
            form = ContactForm()
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = ContactForm(initial=initial)

    return render(request, "store/contact.html", {"form": form})
