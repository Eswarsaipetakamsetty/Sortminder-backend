from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, UserProfileView, LogoutView, CustomLoginView, LeaderboardView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/",CustomLoginView.as_view() , name="custom_login"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard")
]
