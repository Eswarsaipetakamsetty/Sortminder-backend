from django.urls import path
from .views import UserScoreGraphView

urlpatterns = [
    path("score-progress/", UserScoreGraphView.as_view(), name="user-score-progress"),
]
