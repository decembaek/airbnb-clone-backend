# 로그인 관련 호출 login
from django.contrib.auth import authenticate, login, logout
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated  # 권한

from . import serializers
from .models import User

import jwt
import requests


class Me(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(
            user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            user = serializer.save()
            serializer = serializers.PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class Users(APIView):
    def post(self, request):
        password = request.data.get("password")
        if not password:
            raise ParseError
        serializer = serializers.PrivateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # set_password Django 패스워드 만들기 HASH 해쉬로 만들기
            user.set_password(password)
            user.save()
            serializer = serializers.PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class PublicUser(APIView):
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        # 추후에 Public으로 바꾸기
        # 1. 사용자들이 내가 남긴 리뷰들을 볼수있게
        # 2. 내가 얼마나 집을 가지고 있는지
        # 3. 내가 어떤 도시들을 여행했는지
        # 4. 내게 남긴 리뷰들을 볼 수 있게 만들기
        except User.DoesNotExist:
            raise NotFound
        serializer = serializers.PrivateUserSerializer(user)
        return Response(serializer.data)


# PUT
class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            raise ParseError
        # Django Hash 해쉬 비밀번호 확인하기 True면 일치
        if user.check_password(old_password):
            # Hash로 비번 저장
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# 로그인때 사용하는 로직
class LogIn(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            return Response({"ok": "welcome"})
        else:
            return Response({"error": "비밀번호가 틀렸습니다."})


# LogOut 만들기 로그아웃 함수


class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": "로그아웃 되었습니다"})


# install pyjwt 설치하기 JWT 로직
class JWTLogIn(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            raise ParseError
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            # 유저가 토큰을 볼수있으니 중요한 정보는 넣으면 안됌
            # 대신 수정은 불가능함
            # 토큰 암호화
            token = jwt.encode(
                {"pk": user.pk},
                settings.SECRET_KEY,  # 비밀키 (서명)
                algorithm="HS256",  # 업계 표준 암호화
            )
            return Response({"token": token})
        else:
            return Response({"error": "비밀번호가 틀렸습니다."})


class GithubLogIn(APIView):

    def post(self, request):
        code = request.data.get("code")
        accsess_token = requests.post(
            f"https://github.com/login/oauth/access_token?code={code}&client_id=52023d9e05ce9e891654&client_secret={settings.GH_SECRET}",
            headers={"Accept": "application/json"},
        )
        accsess_token = accsess_token.json().get("access_token")
        user_data = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {accsess_token}",
                "Accept": "application/json",
            },
        )
        user_data = user_data.json()
        user_emails = requests.get(
            "https://api.github.com/emails",
            headers={
                "Authorization": f"Bearer {accsess_token}",
                "Accept": "application/json",
            },
        )
        user_emails = user_emails.json()
        return Response()
