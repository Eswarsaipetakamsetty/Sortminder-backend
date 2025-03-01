from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .models import UserProgress
from .serializers import UserProgressGraphSerializer

class UserScoreGraphView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        print(user)

        # Filter only completed challenges where `result=True` and `completed_at` is NOT NULL
        completed_challenges = UserProgress.objects.filter(
            user=user, 
            result=True
        ).exclude(completed_at=None).order_by("completed_at")

        print(completed_challenges)

        if not completed_challenges.exists():
            return Response([], status=status.HTTP_200_OK)  # Return an empty list instead of 404

        serializer = UserProgressGraphSerializer(completed_challenges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

