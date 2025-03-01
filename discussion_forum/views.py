from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DiscussionForumMessage, DiscussionForumReply
from .serializers import MessageSerializer, ReplySerializer
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status

class DiscussionMessageListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        messages = DiscussionForumMessage.objects.all().order_by("-created_at")

        paginator = Paginator(messages, 10)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        serializer = MessageSerializer(page_obj, many=True)
        return Response({
            "messages" : serializer.data,
            "total_pages" : paginator.num_pages,
            "current_page" : int(page_number)
        })
    

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ReplyListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        message = get_object_or_404(DiscussionForumMessage, id=request.data.get("message"))
        serializer = ReplySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, message=message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LikeMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, message_id):
        message = get_object_or_404(DiscussionForumMessage, id=message_id)

        if request.user and message.likes.all():
            return Response({"message": "Message already liked"}, status=status.HTTP_200_OK)
        
        message.likes.add(request.user)
        return Response({"message": "Message liked successfully"}, status=status.HTTP_200_OK)

class LikeReplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, reply_id):
        reply = get_object_or_404(DiscussionForumReply, id=reply_id)

        if request.user in reply.likes.all():
            return Response({"message": "Reply already liked"}, status=status.HTTP_200_OK)
        
        reply.likes.add(request.user)
        return Response({"message": "Reply liked successfully"}, status=status.HTTP_200_OK)
    
class CheckLikeForMessage(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, message_id):
        message = get_object_or_404(DiscussionForumMessage, id=message_id)
        if request.user in message.likes.all():
            return Response({"liked" : True}, status=status.HTTP_200_OK)
        return Response({"liked" : False}, status=status.HTTP_200_OK)
    
class CheckLikeForReply(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reply_id):
        reply = get_object_or_404(DiscussionForumReply, id=reply_id)
        if request.user in reply.likes.all():
            return Response({"liked" : True}, status=status.HTTP_200_OK)
        return Response({"liked" : False}, status=status.HTTP_200_OK)