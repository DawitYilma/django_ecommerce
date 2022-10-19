from dataclasses import field
from django import forms
from django.contrib.auth.models import User
from ecommerce.models import Customer

class CustomerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')