"""Edutube views."""

# Django
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.files.images import ImageFile
from django.core.mail import send_mail, EmailMultiAlternatives
from django.db.models import F, Window, Sum, Case, When, CharField, Value, DurationField, ExpressionWrapper, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, Count
from django.db.models.functions import Rank, Cast
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django_cte import CTEManager, With

# Functions
from videos import functions

# Models
from django.contrib.auth.models import User
from videos.models import Video, Comment
from users.models import Profile, Country, Notification, Team

# Utils
import ast

# Vista del Home
class HomeView(TemplateView):
    template_name = 'home.html'
    

class UsernameDetailView(DetailView):
    # Username Detail View

    template_name = "users/detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"
    queryset = User.objects.all()
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        # Add user's videos
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        profile = Profile.objects.get(user=user.id)

        if not(self.request.user.is_anonymous):
            my_profile = Profile.objects.get(user=self.request.user.id)
            subscription = my_profile.subscriptions.all()
            if my_profile in subscription:
                subscription = True
            else:
                subscription = False
        else:
            subscription = False

        look_videos = Video.objects.filter(profile=profile).annotate(count=Count('id'))

        week_duration = timezone.now() - timezone.timedelta(weeks=1)
        
        look_new_videos = look_videos.annotate(
            time_ago=ExpressionWrapper(
                timezone.now() - F("created"),
                output_field=DurationField()
            )
        ).order_by('created')


        #list_words = users_translations.detail_translation(language)

        team = profile.team
        if team:
            team_members = Profile.objects.filter(team=team).annotate(
                if_owner=Case(
                    When(id=team.owner.id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ))
            context["team_members"] = team_members


        context["look_videos"] = look_videos
        context["look_new_videos"] = look_new_videos
        context["subscription"] = subscription
        context["videos"] = look_videos
        
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        profile = Profile.objects.get(id=user.id)
        my_user = self.request.user
        my_profile = Profile.objects.get(id=my_user.id)
        
        action = self.request.POST.get("action", None)
        search_user = self.request.POST.get("user", None)
        option = self.request.POST.get("option", None)
        show_team_members = self.request.POST.get("show_team_members", None)
        member = self.request.POST.get("member", None)
        team_id = self.request.POST.get("team_id", None)

        if action:
            if action == "subscribed":
                if user != my_user:
                    profile.subscribers.add(my_profile)
                    my_profile.subscriptions.add(profile)
                    notification = Notification.objects.create(profile=profile,
                                                action=f"subscribed",
                                                parameter=my_user.username,
                                                option="Profile",
                                                profile_parameter=my_profile
                                                )
            elif action == "unsubscribed":
                if user != my_user:
                    profile.subscribers.remove(my_profile)
                    my_profile.subscriptions.remove(profile)
                    try:
                        notification = Notification.objects.get(profile=profile,
                                                action=f"unsubscribed",
                                                parameter=self.request.user.username,
                                                    )
                        notification.delete()
                    except:
                        pass
            return super().get(request, *args, **kwargs)
        
        elif show_team_members:
            team = Team.objects.get(id=team_id)
            team_members = Profile.objects.filter(team=team).annotate(
                if_owner=Case(
                    When(id=team.owner.id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ))
            
            if member:
                team_members = team_members.filter(user__username__icontains=member)

            players = list(team_members.values("id", "user__username", "user__id", "picture", "if_owner"))
            return JsonResponse(players, safe=False)
        elif user:
            if search_user == "":
                if option == "subscribers":
                    users = profile.followers.all()
                    users = list(users.values("user__id", "picture", "user__username"))
                elif option == "subscriptions":
                    users = profile.followings.all()
                    users = list(users.values("user__id", "picture", "user__username"))
                elif option == "members":
                    users = users = Profile.objects.filter(team=profile.team).annotate(
                        if_owner=Case(
                            When(id=user.profile.team.owner.id, then=Value(True)),
                            default=Value(False),
                            output_field=BooleanField(),
                        ))
                    users = list(users.values("user__id", "picture", "user__username", "if_owner"))
            else:
                if option == "subscribers":
                    users = profile.subscribers.filter(user__username__icontains=search_user)
                    users = list(users.values("user__id", "picture", "user__username"))
                elif option == "subscriptions":
                    users = profile.subscribers.filter(user__username__icontains=search_user)
                    users = list(users.values("user__id", "picture", "user__username"))
                elif option == "members":
                    users = Profile.objects.filter(team=profile.team).annotate(
                        if_owner=Case(
                            When(id=profile.team.owner.id, then=Value(True)),
                            default=Value(False),
                            output_field=BooleanField(),
                        )).filter(user__username__icontains=search_user)
                    users = list(users.values("user__id", "picture", "user__username", "if_owner"))
            return JsonResponse(users, safe=False)