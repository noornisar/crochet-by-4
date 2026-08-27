from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .form import UserRegisterForm, UserLoginForm


def register(request):

    if request.method == "POST":

        form = UserRegisterForm(request.POST)

        if form.is_valid():

            form.save()

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