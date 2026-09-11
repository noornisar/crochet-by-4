from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from .form import UserRegisterForm, UserLoginForm
from store.services.email_service import send_welcome_email


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Safely send welcome email
            host = request.get_host()
            try:
                current_site = get_current_site(request)
                domain = current_site.domain if (current_site and current_site.domain != 'example.com') else host
            except Exception:
                domain = host or '127.0.0.1:8000'

            send_welcome_email(user, site_domain=domain)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("account:login")
    else:
        form = UserRegisterForm()

    return render(request, "store/account/register.html", {"form": form})


def user_login(request):

    if request.method == "POST":

        form = UserLoginForm(request, data=request.POST)

        if form.is_valid():

            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                return redirect("store:all_products")  # Change to your home URL name

    else:

        form = UserLoginForm()

    return render(request, "store/account/login.html", {"form": form})


def user_logout(request):

    logout(request)

    return redirect("store:all_products") # Change to your home URL name