from django.db import models
from django.conf import settings

class DiscussionForumMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_messages", blank=True)

    def total_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"
    
class DiscussionForumReply(models.Model):
    message = models.ForeignKey(DiscussionForumMessage, on_delete=models.CASCADE, related_name="replies")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="liked_replies", blank=True)

    def total_likes(self):
        return self.likes.count()
    
    def __str__(self):
        return f"Reply by {self.user.username} on {self.message.id}"
