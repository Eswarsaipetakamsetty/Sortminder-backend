from rest_framework.request import Request
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

def get_user_from_ctx(request):
    jwt_auth = JWTAuthentication()
    try:
        user, _ = jwt_auth.authenticate(request)
        return user
    except Exception:
        return None