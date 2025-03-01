from django.urls import path
from .views import StartChallengeView, RunCodeView, SubmitCodeView

urlpatterns = [
    path('start_challenge/', StartChallengeView.as_view(), name='start_challenge'),
    path('run_code/', RunCodeView.as_view(), name='run_code'),
    path('submit_code/', SubmitCodeView.as_view(), name='submit_code')
]
