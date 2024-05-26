# Django
from django.contrib.auth.models import User
from django.db import models
from django_cte import CTEManager

# Utils
from enum import Enum
import typing


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    youtube_channel = models.URLField(max_length=200, blank=True, null=True)
    twitter = models.URLField(max_length=200, blank=True, null=True)
    twitch = models.URLField(max_length=200, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    picture = models.ImageField(upload_to="users/pictures", blank=True, null=True, max_length=500)
    banner = models.ImageField(upload_to="users/pictures", blank=True, null=True, max_length=500)
    country = models.ForeignKey("Country", on_delete=models.CASCADE, blank=True, null=True)
    team = models.ForeignKey("Team", on_delete=models.CASCADE, blank=True, null=True)

    subscribers = models.ManyToManyField('self', related_name='subscriptions', blank=True, symmetrical=False)

    verified = models.BooleanField(blank=True, null=True)

    language_choices = (("English", "English"),
                           ("Spanish", "Spanish"),
                           ("Russian", "Russian"),
                           ("German", "German"),
                           ("Czech", "Czech"))
    language = models.CharField(max_length=12, choices=language_choices, default="English")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Country(models.Model):
    
    objects = CTEManager()
    
    country = models.CharField(max_length=200, blank=True)

    picture = models.FileField(upload_to="countries/pictures", blank=True, null=True)

    abbreviation = models.CharField(max_length=3, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return country
        return self.country
    
    class Meta:
        verbose_name_plural = "Countries"

class Team(models.Model):
    
    objects = CTEManager()
    
    name = models.CharField(max_length=400, blank=True)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name="owner")
    members = models.ManyToManyField(User, blank=True, null=True, related_name="members")

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return name
        return self.name
    
class TeamInvitation(models.Model):
    
    objects = CTEManager()
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Return team
        return self.team.name

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user")

    action_choices = (("video_accepted", "video_accepted"),
                    ("video_rejected", "video_rejected"),
                    ("video_under_consideration", "video_under_consideration"),
                    ("subscription", "subscription"),
                    ("team_invitation", "team_invitation"),
                    )
    action = models.CharField(max_length=500, blank=True, choices=action_choices)
    parameter = models.CharField(max_length=500, blank=True, null=True)
    
    read = models.BooleanField(default=False)

    id_team_parameter = models.IntegerField(null=True, blank=True)
    video_parameter = models.CharField(max_length=500, blank=True, null=True)
    user_parameter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="user_parameter")

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Return action
        return self.action