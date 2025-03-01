from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from challenges.models import Challenges
from django.utils.timezone import now

class UserProgress(models.Model):
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenges, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    attempts = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    result = models.BooleanField(default=False)
    score_increase = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.status})"
    
class UserChallengeSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenges, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, unique=True)
    start_time = models.DateTimeField(default=now)

    def __str__(self):
        return f"Session {self.session_id} - {self.user.username}"
