# Django

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth import password_validation
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import connection
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, FloatField, Count
from django.db.models.expressions import RawSQL
from django.db.models.functions import Rank, Lag, Lead
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy, resolve, Resolver404, get_resolver
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, FormView, UpdateView, TemplateView
from django.views.generic.base import View
from django_cte import CTEManager, With

# Functions
from videos import functions


# Models
from users.models import Profile, Country, Notification, Team, TeamInvitation
from videos.models import Video, Comment

# Forms
from users.forms import SignupForm, CustomAuthenticationForm

# Utils
import ast
import asyncio
import re


class ReadNotifications(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        profile = Profile.objects.get(user=request.user.id)
        notifications = Notification.objects.filter(profile=profile)
        for notification in notifications:
            notification.read = True
            notification.save()

        response_data = {'success': True,}

        return JsonResponse(response_data)

# Vista para Login
class LoginView(auth_views.LoginView):
    # Login View

    template_name = "users/login.html"
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    # Vista de Logout
    pass

# Vista para Registrarse
class SignupView(FormView):
    # Users sign up view

    template_name = 'users/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["help_text"] = password_validation.password_validators_help_text_html()
        return context

    def form_valid(self, form):
        # Save form data
        form.save()
        return super().form_valid(form)


# Vista para Editar tu Perfil
class UpdateProfileView(LoginRequiredMixin, TemplateView):

    template_name = 'users/update_profile.html'

    def get_object(self):
        profile = Profile.objects.filter(user=self.request.user.id)
        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()


        countries = Country.objects.order_by("country")

        context["countries"] = countries
        return context

    def post(self, request, *args, **kwargs):

        user = self.request.user
        profile = user.profile
        error_message = None

        username = self.request.POST.get("username")
        country = self.request.POST.get("country")
        youtube_channel = self.request.POST.get("youtube_channel")
        twitter = self.request.POST.get("twitter")
        twitch = self.request.POST.get("twitch")
        facebook = self.request.POST.get("facebook")

        delete_picture = self.request.POST.get("delete_picture")
        delete_banner = self.request.POST.get("delete_banner")

        if delete_picture:
            old_picture = profile.picture.path if profile.picture else None
            if old_picture and default_storage.exists(old_picture):
                default_storage.delete(old_picture)
            profile.picture = None
            profile.save()
            return JsonResponse({"success": True})
            
        if delete_banner:
            old_banner = profile.banner.path if profile.banner else None
            if old_banner and default_storage.exists(old_banner):
                default_storage.delete(old_banner)
            profile.banner = None
            profile.save()
            return JsonResponse({"success": True})

        username_taken = User.objects.filter(username=username).exists()
        if not username:
            error_message = "The username cannot be empty."
        elif len(username) > 20:
            error_message = "Username must be at most 20 characters long"
        elif not re.match("^\w+$", username):
            error_message = "Username must be alphanumeric"
        elif ' ' in username or '/' in username:
            error_message = "Username cannot contain spaces or '/'"
        elif username_taken and not(self.request.user.username == username):
            error_message = "The username is already in use. Please choose another."
        else:
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

            is_error = False

            for pattern in urls:
                if re.match(pattern, username):
                    is_error = True
            
            if is_error:
                error_message = "The username is already in use. Please choose another."
            else:
                user.username = username
                user.save()
        try:
            picture = self.request.FILES["picture"]
            if picture is not None and functions.is_valid_image(picture):
                old_picture = profile.picture.path if profile.picture else None
                if old_picture and default_storage.exists(old_picture):
                    default_storage.delete(old_picture)
                file_path = default_storage.save(f"users/pictures/{profile.id}/{picture.name}", ContentFile(picture.read()))
                profile.picture = file_path
        except:
            pass
        try:
            if self.request.global_context["is_subscriber"]:
                banner = self.request.FILES["banner"]
                if banner is not None and functions.is_valid_image(banner):
                    old_banner = profile.banner.path if profile.banner else None
                    if old_banner and default_storage.exists(old_banner):
                        default_storage.delete(old_banner)
                    banner_path = default_storage.save(f"users/pictures/{profile.id}/{banner.name}", ContentFile(banner.read()))
                    profile.banner = banner_path
        except:
            pass
        try:
            country = Country.objects.get(country=country)
            profile.country = Country.objects.get(country=country)
        except:
            pass
        if not(youtube_channel == "https://www.youtube.com/@") and (youtube_channel[:25] == "https://www.youtube.com/@"):
            profile.youtube_channel = youtube_channel
        else:
            profile.youtube_channel = ""
        if not(twitter == "https://twitter.com/") and (twitter[:20] == "https://twitter.com/"):
            profile.twitter = twitter
        else:
            profile.twitter = ""
        if not(twitch == "https://twitch.tv/") and (twitch[:18] == "https://twitch.tv/"):
            profile.twitch = twitch
        else:
            profile.twitch = ""
        if not(facebook == "https://facebook.com/") and (facebook[:21] == "https://facebook.com/"):
            profile.facebook = facebook
        else:
            profile.facebook = ""
        if len(self.request.POST.get("bio")) <= 100:
            profile.bio = self.request.POST.get("bio")
        profile.save()

        countries = Country.objects.all().order_by("country")

        return render(
        request,
        'users/update_profile.html',
        {'error_message': error_message, 'countries': countries}
    )