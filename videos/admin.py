# Django
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

# Models
from videos.models import Video, Comment

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    # Video admin

    list_display = ("pk", "profile", "created", "title", "type", "grade")
    search_fields = ("profile", "title", "description")
    ordering = ("-id",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Comment admin."""

    list_display = ('id', 'video', 'profile', 'likes')
    search_fields = ('comment',)
