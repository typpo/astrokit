from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm as AuthForm
from django.utils.translation import ugettext as _


class RegistrationForm(forms.ModelForm):
    """Form for registeration
    Author: Amr Draz
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'type': 'text'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'type': 'email'}))
    password = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'type': 'password'}))

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data):
            raise forms.ValidationError(_('A user with this username already exists'))
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data):
            raise forms.ValidationError(_('A user with this email already exists'))
        return data

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class AuthenticationForm(AuthForm):
    """Form for authentication
    Author: Amr Draz
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'type': 'text'}))
    password = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'type': 'password'}))