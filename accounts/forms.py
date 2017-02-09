from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm as AuthForm
from django.utils.translation import ugettext as _
from django.core.mail import send_mail

import datetime

from settings import SERVER_EMAIL
from .models import URLCode

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


class ForgotPasswordForm(forms.Form):
    """Send email for reseting password
    Author: Amr Draz
    """
    email = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'type': 'email'}))

    def clean_email(self):
        data = self.cleaned_data['email']
        if not User.objects.filter(email=data):
            raise forms.ValidationError(_('A user with this email does not exists'))
        return data


    def send_email(self, request):
        email = self.cleaned_data['email']
        url_code = URLCode(user=User.objects.get(email=email))
        url_code.save()
        link = request.META['HTTP_HOST'] + '/accounts/reset-password/?code=' + url_code.code
        send_mail(
            _('ASTROKIT Reset password'),
            _('Hello There,\nPlease follow the link below to reset your password\n') + link,
            SERVER_EMAIL,
            [email],
            fail_silently=False,
        )


class ResetPasswordForm(forms.Form):
    """Reset password using a forgot password generated link
    Author: Amr Draz
    """
    password = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control', 'type': 'password'}))

    def reset_password(self, user):
        password = self.cleaned_data['password']
        user.set_password(password)
