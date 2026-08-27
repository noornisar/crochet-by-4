from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class UserRegisterForm(UserCreationForm):

    class Meta:

        model = User

        fields = (
            'username',
            'password1',
            'password2',
        )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Enter username'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Create password'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Confirm password'
        })
    )


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"Enter your username"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class":"form-control",
            "placeholder":"Enter your password"
        })
    )    