import uuid
import requests
import base64
import time
from django.core.cache import cache
from django.utils.timezone import now, timedelta
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Challenges, TestCases
from progress.models import UserProgress, UserChallengeSession
from .serializers import ChallengeSerializer
from users.models import User
import logging
import json

logger = logging.getLogger(__name__)

JUDGE0_BASE_URL = "http://localhost:2358"
JUDGE0_SUBMISSION_URL = f"{JUDGE0_BASE_URL}/submissions/"
JUDGE0_BATCH_SUBMISSION_URL = f"{JUDGE0_BASE_URL}/submissions/batch"
JUDGE0_HEADERS = {"Content-Type" : "application/json"}

POLLING_INTERVAL = 2
MAX_ATTEMPTS = 10
CHALLENGE_TIME_LIMIT = timedelta(hours=3)

def create_submission(source_code, language_id, testcases, base64_encode=False):
    submissions = []

    for testcase in testcases:
        submission = {
            "source_code" : base64.b64encode(source_code.encode()).decode() if base64_encode else source_code,
            "language_id" : language_id,
            "stdin" : base64.b64encode(testcase.input.encode()).decode() if base64_encode else testcase.input,
            "expected_output" : base64.b64encode(testcase.expected_output.encode()).decode() if base64_encode else testcase.expected_output
        }
        submissions.append(submission)
    return submissions

def poll_submission_results(tokens):
    attempt = 0
    while attempt < MAX_ATTEMPTS:
        response = requests.get(
            JUDGE0_BATCH_SUBMISSION_URL,
            params={"tokens": ",".join(tokens), "base64_encoded": "false", "fields": "token,stdout,stderr,status_id"},
            headers=JUDGE0_HEADERS
        )

        if response.status_code == 200:
            results = response.json()["submissions"]
            if all(r["status_id"] >= 3 for r in results):
                return results
        
        time.sleep(POLLING_INTERVAL)
        attempt += 1
    return None


class StartChallengeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        difficulty = request.data.get("difficulty")
        if difficulty not in ["beginner", "intermediate", "advanced"]:
            logger.error("invalid request body")
            return Response({"error" : "invalid request body"}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f"user_session:{request.user.username}"
        active_session = cache.get(cache_key)

        if active_session:
            session_data = json.loads(active_session)
            return Response({
                "session_id" : session_data["session_id"],
                "challenge" : session_data["challenge"]
            }, status=status.HTTP_200_OK)
        
        challenge = Challenges.objects.filter(difficulty=difficulty).order_by("?").first()
        if not challenge:
            return Response({"error" : "No challenges available"}, status=status.HTTP_404_NOT_FOUND)

        session_id = str(uuid.uuid4())
        session = UserChallengeSession.objects.create(
            user = request.user,
            challenge = challenge,
            session_id = session_id,
            start_time = now(),
        )

        request.user.is_active_contest = True
        request.user.save()

        session_data = {
            "session_id": session_id,
            "challenge": ChallengeSerializer(challenge).data
        }
        cache.set(cache_key, json.dumps(session_data), 30*60)

        return Response({"session_id" : session_id, "challenge" : ChallengeSerializer(challenge).data}, status=status.HTTP_201_CREATED)
    
class RunCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        code = request.data.get("code")
        print(code)
        language_id = request.data.get("language_id")

        if not session_id or not code or not language_id:
            return Response({"error" : "missing session_id or code or language_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = UserChallengeSession.objects.get(session_id=session_id, user=request.user)
        except UserChallengeSession.DoesNotExist:
            return Response({"error" : "Invalid session_id"}, status=status.HTTP_404_NOT_FOUND)
        
        if now() - session.start_time > CHALLENGE_TIME_LIMIT:
            session.save()
            return Response({"error": "Challenge time limit exceeded"}, status=status.HTTP_403_FORBIDDEN)
        
        challenge = session.challenge
        testcases = TestCases.objects.filter(challenge=challenge, is_hidden=False)
        if not testcases.exists():
            return Response({"error" : "No public testcases found"}, status=status.HTTP_404_NOT_FOUND)
        

        submissions = create_submission(code, language_id, testcases)
        response = requests.post(JUDGE0_BATCH_SUBMISSION_URL, json={"submissions" : submissions}, headers=JUDGE0_HEADERS)

        if response.status_code == 201:
            tokens = [item["token"] for item in response.json()]
            results = poll_submission_results(tokens)
            if results:
                return Response({"session_id" : session_id, "results" : results})
            else:
                return Response({"error" : "submission polling timed out."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        else:
            return Response({"error" : "failed to submit code to judge0"}, status=response.status_code)
    
class SubmitCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.data.get("session_id")
        code = request.data.get("code")
        language_id = request.data.get("language_id")

        if not session_id or not code or not language_id:
            return Response({"error" : "missing session_id or code or language_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = UserChallengeSession.objects.get(session_id=session_id, user=request.user)
        except UserChallengeSession.DoesNotExist:
            return Response({"error" : "Invalid session_id"}, status=status.HTTP_404_NOT_FOUND)
        
        if now() - session.start_time > CHALLENGE_TIME_LIMIT:
            session.save()
            request.user.is_active_contest = False
            request.user.save()
            progress.status = "completed"
            progress.result = False
            progress.completed_at = now()
            progress.save()
            return Response({"error": "Challenge time limit exceeded"}, status=status.HTTP_403_FORBIDDEN)
        
        challenge = session.challenge
        testcases = TestCases.objects.filter(challenge=challenge, is_hidden=True)  #hidden test cases for submit code route

        print(testcases)

        if not testcases.exists():
            return Response({"error" : "No private testcases found"}, status=status.HTTP_404_NOT_FOUND)
        
        submissions = create_submission(code, language_id, testcases)
        print(submissions)
        response = requests.post(JUDGE0_BATCH_SUBMISSION_URL, json={"submissions" : submissions}, headers=JUDGE0_HEADERS)

        if response.status_code == 201:
            tokens = [item["token"] for item in response.json()]
            print(tokens)
            results = poll_submission_results(tokens)
            if results:
                print(results)
                all_passed = all(result["status_id"] == 3 and not result["stderr"] for result in results)

                progress, created = UserProgress.objects.get_or_create(user=request.user, challenge=session.challenge)
                if all_passed:
                    progress.status = "completed"
                    progress.attempts += 1
                    progress.save()
                    profile = User.objects.get(username=request.user.username)
                    profile.score += challenge.points
                    profile.is_active_contest = False
                    profile.problems_solved += 1
                    profile.save()
                    progress.status = "completed"
                    progress.completed_at = now()
                    progress.result = True
                    progress.score_increase = challenge.points
                    progress.save()
                    cache.delete(f"user_session:{request.user.username}")
                    return Response({"message" : "All test cases passed. Challenge completed!", "results" : results})
                else:
                    progress.attempts += 1
                    progress.save()
                    return Response({"message" : "some test cases failed. Try again.", "results" : results})
            else:
                return Response({"error" : "submission polling timed out."}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        else:
            return Response({"error": "Failed to submit code to Judge0."}, status=response.status_code)