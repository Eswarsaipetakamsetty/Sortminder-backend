from django.urls import path
from .views import DiscussionMessageListView, ReplyListView, LikeMessageView, LikeReplyView, CheckLikeForMessage, CheckLikeForReply

urlpatterns = [
    path("messages/", DiscussionMessageListView.as_view(), name="discussion-list"),
    path("messages/reply/", ReplyListView.as_view(), name="reply-list"),
    path("messages/<int:message_id>/like/", LikeMessageView.as_view(), name="like-message"),
    path("replies/<int:reply_id>/like/", LikeReplyView.as_view(), name="like-reply"),
    path("message/<int:message_id>/liked", CheckLikeForMessage.as_view(), name="check-like-for-message"),
    path("reply/<int:reply_id>/liked", CheckLikeForReply.as_view(), name="check-like-for-reply")
]
