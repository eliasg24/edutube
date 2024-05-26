# Django
from django import forms

# Models
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponseBadRequest
from django.template import loader
from django.template.loader import render_to_string
from django.urls import resolve, get_resolver, Resolver404
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from users.models import Profile

# Utils
from django_recaptcha.fields import ReCaptchaField
import re
import unicodedata

UserModel = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username or Email')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            # If the username contains '@', consider it an email and validate it
            try:
                user = UserModel.objects.get(email=username)
            except UserModel.DoesNotExist:
                raise ValidationError("No user found with this email address.")
            return user.username
        return username

class SignupForm(forms.Form):
    # Signup Form
    username = forms.CharField(label=False, min_length=4, max_length=20, widget = forms.TextInput(attrs={'placeholder':'Username', 'onkeyup': 'without_space(this);'}))
    password = forms.CharField(label=False, max_length=70, widget = forms.PasswordInput(attrs={'placeholder':'Password'}))
    password_confirmation = forms.CharField(label=False, max_length=70, widget = forms.PasswordInput(attrs={'placeholder':'Password confirmation'}))
    email = forms.CharField(label=False, min_length=6, max_length=70, widget = forms.EmailInput(attrs={'placeholder':'Email'}))

    def clean_username(self):
        # Username must be unique
        username = self.cleaned_data["username"]
        if not username:
            raise ValidationError("The username cannot be empty.")
        if len(username) > 20:
            raise forms.ValidationError("Username must be at most 20 characters long")
        if not re.match("^\w+$", username):
            raise forms.ValidationError("Username must be alphanumeric")
        if ' ' in username or '/' in username:
            raise forms.ValidationError("Username cannot contain spaces or '/'")
        username_taken = User.objects.filter(username=username).exists()
        if username_taken:
            raise forms.ValidationError("Username is already in use")

        resolver = get_resolver()

        # Obtener todas las URLs
        urls = []
        for url_pattern in resolver.url_patterns:
            if hasattr(url_pattern, 'url_patterns'):  # Verificar si es un include()
                for sub_url_pattern in url_pattern.url_patterns:
                    if hasattr(sub_url_pattern, 'pattern'):
                        url = sub_url_pattern.pattern.describe()
                        url_without_name = url.split('[name=')[0].strip().strip("'")
                        urls.append(url_without_name)

        # Crear una respuesta con la lista de URLs


        urls.remove('')
        urls.remove('')
        urls.remove('')

        for pattern in urls:
            if re.match(pattern, username):
                raise forms.ValidationError("Username is not available")

        return username

    def clean(self):
        # Verify password confirmation match
        data = super().clean()

        password = data["password"]
        password_confirmation = data["password_confirmation"]

        if password != password_confirmation:
            raise forms.ValidationError("Passwords do not match")
        
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long and include at least one digit and one uppercase letter.")

        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must be at least 8 characters long and include at least one digit and one uppercase letter.")

        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must be at least 8 characters long and include at least one digit and one uppercase letter.")

        return data

    def save(self):
        # Create user and profile
        data = self.cleaned_data
        data.pop("password_confirmation")

        user = User.objects.create_user(**data)
        profile = Profile(user=user.id)
        profile.save()
