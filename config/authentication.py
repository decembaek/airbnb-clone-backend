# 유저 인증 로직 만들어보기 Auth
# 인증 로직을 보는 용도(공부)기 때문에 보안에 주의 필요
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User

import jwt
from django.conf import settings


class TrustMeBroAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # headers 헤더에 내용 추가해서 받기
        username = request.headers.get("Trust-Me")
        if not username:
            return None
        try:
            user = User.objects.get(username=username)
            return (user, None)  # 뒤에 None은 규칙이기 때문
        except User.DoesNotExist:
            raise AuthenticationFailed(f"No user {username}")


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Jwt")
        if not token:
            return None
        # 암호 해제하는 방법
        decoded = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms="HS256",
        )
        pk = decoded.get("pk")
        if not pk:
            raise AuthenticationFailed("사용자 계정 PK가 없습니다.")
        try:
            user = User.objects.get(pk=pk)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed("사용자를 찾을수 없습니다.")
        return None
