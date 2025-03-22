from django.contrib.auth.forms import AuthenticationForm
from django import forms


class AuthenticationFormWithBS(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'password'})
    )
    
    # class Meta:
    #     widgets = {
    #         'username': forms.TextInput(attrs={'class': 'form-control'}),
    #         'password': forms.PasswordInput(attrs={'class': 'form-control'})
    #     }
