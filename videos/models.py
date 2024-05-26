# Django
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django_cte import CTEManager

# Models
from users.models import Profile

# Utils
from enum import Enum
import typing


class Video(models.Model):
    
    uu_id = models.CharField(max_length=200, blank=True)

    title = models.CharField(max_length=255)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    sector_choices = (("Grado Educativo", "Grado Educativo"),
                    ("Educación Libre", "Educación Libre"),
                    )
    sector = models.TextField(choices=sector_choices, default="Educación Libre")
    
    type_choices = (("Fisica", "Fisica"),
                    ("Matematicas", "Matematicas"),
                    ("Programacion", "Programacion"),
                    ("Filosofia", "Filosofia"),
                    ("Psicologia", "Psicologia"),
                    ("Ingles", "Ingles"),
                    )
    type = models.TextField(choices=type_choices, blank=True, null=True)
    
    grade_choices = (("1° grado", "1° grado"),
                    ("2° grado", "2° grado"),
                    ("3° grado", "3° grado"),
                    ("4° grado", "4° grado"),
                    ("5° grado", "5° grado"),
                    ("6° grado", "6° grado"),
                    ("7° grado", "7° grado"),
                    ("8° grado", "8° grado"),
                    ("9° grado", "9° grado"),
                    ("1° grado (prepa)", "1° grado (prepa)"),
                    ("2° grado (prepa)", "2° grado (prepa)"),
                    )
    
    grade = models.TextField(choices=grade_choices, blank=True, null=True)

    views = models.IntegerField(null=True, blank=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    rating = models.FloatField(null=True, blank=True)

    new = models.BooleanField(default=False)

    created = models.DateTimeField()
    modified = models.DateTimeField()

    def __str__(self):
        return f"{self.title} - {self.profile}"

class Comment(models.Model):
    
    comment = models.TextField()
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    profile = models.IntegerField(default=0)

    likes = models.ForeignKey(Profile, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.video.title} - {self.profile}"