"""Edutube views."""

# Django
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.files.images import ImageFile
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator
from django.db import models
from django.db.models import F, Window, Sum, Case, When, CharField, Value, ExpressionWrapper, DurationField, Func, IntegerField, BooleanField, Q, OuterRef, Subquery, Count
from django.db.models.functions import Rank, Cast, Extract, Now, Trunc
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
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

# Vista del Feed
class FeedView(ListView):

    template_name = 'videos/feed.html'
    model = Video
    paginate_by = 200
    context_object_name = 'videos'

    def get_queryset(self):

        week_duration = timezone.now() - timezone.timedelta(weeks=1)
        queryset = Video.objects.all().order_by('-id').annotate(time_ago=Now()-F('created')
        ).order_by("created")

        search = self.request.GET.get('search')
        type_filter = self.request.GET.get('type')
        sector_filter = self.request.GET.get('sector')
        grade_filter = self.request.GET.get('grade')

        range_datetime = self.request.GET.get('range_datetime')

        if search:
            queryset = queryset.filter(title__icontains=search)

        if type_filter:
            queryset = queryset.filter(type=type_filter)

        if grade_filter:
            queryset = queryset.filter(grade=grade_filter)

        week_duration = timezone.now() - timezone.timedelta(weeks=1)

        new_videos_queryset = queryset.filter(created__gt=week_duration).update(new=True)

        queryset = queryset.order_by('-created')

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # functions.get_video_info(
        #     "https://www.youtube.com/watch?v=2PFqmlohtps", 
        #     "MIGALA", 
        #     "8° grado",
        #     "Filosofia"
        # )

        search = self.request.GET.get('search')
        type_filter = self.request.GET.get('type')
        sector_filter = self.request.GET.get('sector')
        grade_filter = self.request.GET.get('grade')
        range_datetime = self.request.GET.get('range_datetime')

        videos = self.get_queryset()
        paginator = Paginator(videos, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['has_previous'] = page_obj.has_previous()
        context['has_next'] = page_obj.has_next()
        context['has_other_pages'] = paginator.num_pages > 1
        context['previous_page_number'] = page_obj.previous_page_number
        context['next_page_number'] = page_obj.next_page_number
        context['paginator'] = paginator
        context['number'] = page_obj.number
        context['page_max'] = paginator.num_pages

        context['search'] = search
        context['type_filter'] = type_filter
        context['sector_filter'] = sector_filter
        context['grade_filter'] = grade_filter
        context['range_datetime'] = range_datetime
        return context


# Vista del Detail del Video
class VideoDetailView(DetailView):
    template_name = "videos/detail.html"
    model = Video
    context_object_name = "video"

    def get_object(self, queryset=None):

        return get_object_or_404(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        video = self.get_object()

        comments = Comment.objects.filter(video=video).order_by("created")

        context["comments"] = comments
        return context

    def post(self, request, **kwargs):
        r = request.POST
        demon = self.get_object()
        option = r.get("option", None)

        if option == "show_team_members":

            team = Team.objects.get(id=r.get("id", None))
            team_members = Profile.objects.filter(team=team).annotate(
                if_owner=Case(
                    When(id=team.owner.id, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )).order_by(f"id")

            if r.get("member", None):
                team_members = team_members.filter(user__username__icontains=r.get("member", None))

            players = list(team_members.values("id", "user__username", "user__id", "picture", "if_owner"))
            return JsonResponse(players, safe=False)

        elif option == "by_likes":
            comments = Comment.objects.filter(demon=demon, accepted=True).order_by("likes")

        elif option == "by_datetime":
            comments = Comment.objects.filter(demon=demon, accepted=True).order_by("created")

        comments = list(comments.values("user__username", "player__team__name", "player__country__picture", "player__country__country", "video"))
        comments = list(User.objects.filter())

        return JsonResponse(comments, safe=False)