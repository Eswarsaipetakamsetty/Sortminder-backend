from rest_framework import serializers
from .models import UserProgress

class UserProgressGraphSerializer(serializers.ModelSerializer):
    challenge_title = serializers.CharField(source="challenge.title", read_only=True)  # Get challenge name
    date = serializers.DateTimeField(source="completed_at", format="%Y-%m-%d")  # Format date

    class Meta:
        model = UserProgress
        fields = ["challenge_title", "score_increase", "date"]
