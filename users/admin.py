# Django
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

# Models
from users.models import User, Profile, Country, Notification, Team, TeamInvitation

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Profile admin

    list_display = ("pk", "user", "verified")
    list_display_links = ("pk", "user")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name", "phone")
    list_filter = ("verified", "created", "modified")
    fieldsets = (
        ("Profile", {"fields": ("user", "picture", "banner")}),
        ("Extra info", {"fields": (("youtube_channel", "twitter", "twitch", "facebook", "phone"), "bio", "country", "verified", "language")}),
        ("Teams", {"fields": (("team",))}),
        ("Metadata", {"fields": ("created", "modified")}))
    readonly_fields = ("created", "modified")
    ordering = ("-id",)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Country admin."""

    list_display = ('id', 'country', 'picture', 'abbreviation')
    list_editable = ("picture",)
    search_fields = ('country',)
    list_filter = ('country',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin."""

    list_display = ('id', 'action', 'parameter', "video_parameter", 'read', 'user', 'user_parameter')
    search_fields = ('user__username',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Team admin."""

    list_display = ('id', 'name', 'owner')
    search_fields = ('name',)

@admin.register(TeamInvitation)
class TeamInvitationAdmin(admin.ModelAdmin):
    """TeamInvitation admin."""

    list_display = ('id', 'team', 'user')
    search_fields = ('team',)