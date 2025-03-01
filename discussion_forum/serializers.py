from rest_framework import serializers
from .models import DiscussionForumMessage, DiscussionForumReply

class ReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_profile_photo = serializers.SerializerMethodField()
    total_likes = serializers.IntegerField(read_only=True)

    class Meta:
        model = DiscussionForumReply
        fields = ["id", "message", "user", "user_profile_photo", "content", "created_at", "total_likes"]
    
    def get_user_profile_photo(self, obj):
        return obj.user.profile_photo if obj.user.profile_photo else None

class MessageSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_profile_photo = serializers.SerializerMethodField()
    total_likes = serializers.IntegerField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionForumMessage
        fields = ["id", "user", "user_profile_photo", "content", "created_at", "total_likes", "replies"]
    
    def get_user_profile_photo(self, obj):
        return obj.user.profile_photo if obj.user.profile_photo else None
    
    def get_replies(self, obj):
        replies = obj.replies.all().order_by("-created_at")  # Recent replies first
        return ReplySerializer(replies, many=True).data
