"""Edutube URLs."""

# Django
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

# Views
from Edutube import views
from users import views as users_views
from videos import views as demons_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        route=r'',
        view=demons_views.FeedView.as_view(),
        name='feed'
    ),
    re_path(
        route=r'^home/?$',
        view=views.HomeView.as_view(),
        name='home'
    ),
    re_path(
        route=r'^users/me/?$',
        view=users_views.UpdateProfileView.as_view(),
        name='update_profile'
    ),
    re_path(
        route=r'^video/(?P<uu_id>\d+)/?$',
        view=demons_views.VideoDetailView.as_view(),
        name='video_detail'
    ),
    re_path(
        route=r'^read_notifications/?$',
        view=users_views.ReadNotifications.as_view(),
        name='read_notifications'
    ),
    re_path(
        route=r'^login/?$',
        view=users_views.LoginView.as_view(),
        name='login'
    ),
    re_path(
        route=r'^logout/?$',
        view=users_views.LogoutView.as_view(),
        name='logout'
    ),
    re_path(
        route=r'^signup/?$',
        view=users_views.SignupView.as_view(),
        name='signup'
    ),
    re_path(
        route=r'^(?P<username>[^/]+)/?$',
        view=views.UsernameDetailView.as_view(),
        name='username_detail'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
