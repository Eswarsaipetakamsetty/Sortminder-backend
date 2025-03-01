from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    address = models.TextField(blank=True, null=True)
    college = models.CharField(max_length=255, blank=True, null=True)
    is_creator = models.BooleanField(default=False)
    problems_solved = models.IntegerField(default=0)
    favourite_language = models.CharField(max_length=255, blank=True, null=True)
    score = models.IntegerField(default=0)
    is_active_contest = models.BooleanField(default=False)
    math_score = models.IntegerField(default=0)
    profile_photo = models.CharField(blank=True, null=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    def __str__(self):
        return self.username


