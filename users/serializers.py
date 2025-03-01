from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", 
            "username", 
            "first_name", 
            "last_name", 
            "email", 
            "address", 
            "college",
            "is_creator",
            "problems_solved",
            "favourite_language",
            "score",
            "is_active_contest",
            "math_score",
            "profile_photo",
        ]
        read_only_fields = [
            "id",
            "problems_solved",
            "score",
            "favourite_language",
            "math_score",
        ]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "college",
        ]
        extra_kwargs = {"password": {"write_only" : True}}


    def validate_password(self, value):
        return make_password(value)
    
    def create(self, validated_data):
        return User.objects.create(**validated_data)
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
