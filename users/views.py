from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer, RegisterSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
import uuid
import supabase
from django.conf import settings
import json


SUPABASE_BUCKET = "sortminder-filestorage"
SUPABASE_URL = "https://gtyjozzqkslmsutwzats.supabase.co"

supabase_client = supabase.create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

from . import utils
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = utils.get_user_from_ctx(request)
        if not user:
            return Response({"error" : "Invalid Token or userid not found"}, status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        user = utils.get_user_from_ctx(request)
        if not user:
            return Response({"error" : "Invalid Token or userid not found"}, status.HTTP_401_UNAUTHORIZED)
        
        profile_photo = request.FILES.get("profile_photo")
        print(profile_photo)
        try:
            if profile_photo:
                file_ext = profile_photo.name.split(".")[-1]
                file_name = f"profile_photos/{uuid.uuid4()}.{file_ext}"

                response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(
                    file_name, profile_photo.read(), file_options={"content-type": profile_photo.content_type}
                )
                

                if hasattr(response, "path"):
                    new_profile_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_name}"
                    request.data["profile_photo"] = new_profile_url
                else:
                    return Response({"error" : "upload failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                user.profile_photo = new_profile_url
                user.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(request.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            if not refresh_token:
                return Response({"error" : "Refresh Token required"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error" : "Invalid Token"}, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        logger.warning(f"Received login attempt: username={username}")


        if not username or not password:
            logger.warning("Login failed: Missing Credentials")
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)

        if not user or user is None:
            logger.warning(f"Login failed : Invalid credentials for {username}")
            return Response({"error" : "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            logger.warning(f"Login failed : Inactive user {username}")
            return Response({"error" : "User account is inactive"}, status=status.HTTP_403_FORBIDDEN)
        
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        logger.info(f"User {username} logged in successfully")

        return Response({
            "refresh" : str(refresh),
            "access": str(access),
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "is_creator": user.is_creator,
            "problems_solved": user.problems_solved,
            "favourite_language": user.favourite_language,
            "score": user.score,
            "math_score": user.math_score,
            "profile_photo": user.profile_photo,
        }, status=status.HTTP_200_OK)
    
class LeaderboardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class LeaderboardView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LeaderboardPagination
    permission_classes = [AllowAny]

    filter_backends = [OrderingFilter]
    ordering_fields = ["score", "problems_solved"]
    ordering = ["-score"]

